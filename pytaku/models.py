import uuid
from google.appengine.ext import ndb
from passlib.hash import pbkdf2_sha512
from datetime import datetime


class Title(ndb.Model):
    url = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty()
    site = ndb.StringProperty()
    thumb_url = ndb.StringProperty()
    last_update = ndb.DateTimeProperty(auto_now_add=True)
    chapters = ndb.JsonProperty()  # [{'name': 'Ch.101', 'url': 'http...'}]
    tags = ndb.StringProperty(repeated=True)
    status = ndb.StringProperty()  # ongoing/completed/unknown

    def is_in_read_list(self, user):
        return self.url in user.read_list

    def is_fresh(self):
        # fresh == updated no longer than 1 day ago
        return (datetime.now() - self.last_update).days <= 1

    def update(self, site, name, thumb_url, new_chapters, status, tags):
        self.site = site
        self.name = name
        self.thumb_url = thumb_url
        self.status = status
        self.tags = tags

        # Update next_chapter_url for the chapter that was previously the
        # latest but not anymore
        new_chapters_num = len(new_chapters) - len(self.chapters)
        if new_chapters_num > 0:

            # previously latest chapter that needs updating:
            chapter_url = self.chapters[0]['url']
            chap = Chapter.get_by_url(chapter_url)

            if chap is not None:
                i = new_chapters_num - 1
                chap.next_chapter_url = new_chapters[i]['url']
                chap.put()

        self.chapters = new_chapters

        self.last_updated = datetime.now()  # "refresh" this title
        self.put()
        return self

    @classmethod
    def create(cls, url, site, name, thumb_url, chapters, status, tags):
        obj = cls(url=url, site=site, name=name, thumb_url=thumb_url,
                  chapters=chapters, status=status, tags=tags)
        obj.put()
        return obj

    @classmethod
    def get_by_url(cls, url):
        return cls.query(cls.url == url).get()


class Chapter(ndb.Model):
    url = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    pages = ndb.JsonProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    next_chapter_url = ndb.StringProperty()
    prev_chapter_url = ndb.StringProperty()
    title_url = ndb.StringProperty()

    def is_bookmarked(self, user):
        return self.url in user.bookmarks

    @classmethod
    def create(cls, url, name, pages, title_url, prev, next):
        obj = cls(url=url, name=name, pages=pages, title_url=title_url,
                  prev_chapter_url=prev, next_chapter_url=next)
        obj.put()
        return obj

    @classmethod
    def get_by_url(cls, url):
        return cls.query(cls.url == url).get()


# Email is stored as id to ensure uniqueness
class User(ndb.Model):
    password_hash = ndb.StringProperty()
    api_token = ndb.StringProperty(default=None)
    last_login = ndb.DateTimeProperty(auto_now_add=True)
    read_list = ndb.StringProperty(repeated=True)
    bookmarks = ndb.StringProperty(repeated=True)

    def verify_password(self, password):
        return pbkdf2_sha512.verify(password, self.password_hash)

    def generate_token(self):
        self.api_token = str(uuid.uuid4())

    def logout(self):
        self.api_token = None
        self.put()

    def _add_to_list(self, record, list_name):
        if record.url not in getattr(self, list_name):
            getattr(self, list_name).append(record.url)
            self.put()
            return True
        return False

    def _remove_from_list(self, record, list_name):
        if record.url in getattr(self, list_name):
            getattr(self, list_name).remove(record.url)
            self.put()
            return True
        return False

    def add_to_read_list(self, title):
        return self._add_to_list(title, 'read_list')

    def remove_from_read_list(self, title):
        return self._remove_from_list(title, 'read_list')

    def add_to_bookmarks(self, chapter):
        return self._add_to_list(chapter, 'bookmarks')

    def remove_from_bookmarks(self, chapter):
        return self._remove_from_list(chapter, 'bookmarks')

    @staticmethod
    def hash_password(password):
        return pbkdf2_sha512.encrypt(password)

    @classmethod
    def auth_with_password(cls, email, password):
        user = cls.get_by_id(email)
        if user is not None and user.verify_password(password):
            user.generate_token()
            user.put()
            return user
        else:
            return None

    @classmethod
    def auth_with_token(cls, email, token):
        user = cls.get_by_id(email)
        if user is None or user.api_token is None or user.api_token != token:
            return None, 'invalid_token'
        if (datetime.now() - user.last_login).days > 30:
            return None, 'expired_token'
        return user, None


@ndb.transactional
def createUser(email, password):
    existing = User.get_by_id(email)
    if existing is not None:
        return None

    user = User(id=email, password_hash=User.hash_password(password))
    user.generate_token()
    user.put()
    return user
