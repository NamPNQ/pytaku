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

    def is_in_read_list(self, user):
        return self.key in user.read_list

    def is_fresh(self):
        # fresh == updated less than an hour ago
        return (datetime.now() - self.last_update).seconds < 3600

    def update(self, site, name, thumb_url, chapters):
        self.site = site
        self.name = name
        self.thumb_url = thumb_url
        self.chapters = chapters
        self.last_updated = datetime.now()  # "refresh" this title
        self.put()
        return self

    @classmethod
    def create(cls, url, site, name, thumb_url, chapters):
        obj = cls(url=url, site=site, name=name, thumb_url=thumb_url,
                  chapters=chapters)
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

    def fill_pages(self, pages):
        self.pages = pages
        self.put()

    @classmethod
    def create(cls, url, name, pages, prev, next):
        obj = cls(url=url, name=name, pages=pages,
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
    read_list = ndb.KeyProperty(kind=Title, repeated=True)

    def verify_password(self, password):
        return pbkdf2_sha512.verify(password, self.password_hash)

    def generate_token(self):
        self.api_token = str(uuid.uuid4())

    def logout(self):
        self.api_token = None
        self.put()

    def add_to_read_list(self, title):
        if title.key not in self.read_list:
            self.read_list.append(title.key)
            self.put()
            return True
        return False

    def remove_from_read_list(self, title):
        if title.key in self.read_list:
            self.read_list.remove(title.key)
            self.put()
            return True
        return False

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
