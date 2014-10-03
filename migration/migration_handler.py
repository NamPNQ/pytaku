import webapp2
#from google.appengine.ext import deferred
import importlib


class UpdateHandler(webapp2.RequestHandler):
    def get(self):
        m = importlib.import_module('migration.migrations.00001')
        resp = m.migrate()
        self.response.out.write(unicode(resp))
        self.response.out.write('Schema migration successfully initiated.')

app = webapp2.WSGIApplication([('/update_schema', UpdateHandler)])
