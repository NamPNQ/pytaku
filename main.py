import sys
sys.path.insert(0, 'lib')
import webapp2
from pytaku.api.api import UserHandler, LoginHandler, TitleHandler,\
    SearchHandler, ChapterHandler, TestTokenHandler


app = webapp2.WSGIApplication([
    ('/api/user', UserHandler),
    ('/api/auth', LoginHandler),
    ('/api/title', TitleHandler),
    ('/api/chapter', ChapterHandler),
    ('/api/search', SearchHandler),
    ('/api/test-token', TestTokenHandler),
], debug=True)
