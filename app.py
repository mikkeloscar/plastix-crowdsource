import os
import time

from google.appengine.ext import db

import jinja2
import webapp2

# jinja settings
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
        'views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# DataStore
class Survey(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    ref = db.StringProperty() # HTTP_REFERER
    ip = db.StringProperty() # users IP (used to prevent multiple entries)
    age = db.IntegerProperty()
    gender = db.StringProperty(choices=set(["male", "female"]))
    answer_time = db.IntegerProperty() # time in seconds
    education = db.StringProperty() # education or field
    # experience with latex, programming other?
    latex = db.BooleanProperty(indexed=False, default=False)
    programming = db.BooleanProperty(indexed=False, default=False)

    # exercises
    exercise1 = db.TextProperty(indexed=False)


class Index(webapp2.RequestHandler):

    def get(self):
        # collect some userdata
        referer = self.request.referer
        start_time = int(time.time()) # now unix time

        values = {
            'start_time': start_time,
            'referer': referer
        }

        view = JINJA_ENVIRONMENT.get_template('survey.html')
        self.response.write(view.render(values))


class Answer(webapp2.RequestHandler):

    def post(self):
        start_time = int(self.request.get('start_time'))
        end_time = int(time.time())
        answer_time = end_time - start_time
        ip = self.request.remote_addr

        s = Survey()
        s.ref = self.request.get('referer')
        s.ip = self.request.remote_addr
        try:
            s.age = int(self.request.get('age'))
        except ValueError:
            s.age = 0
        s.gender = self.request.get('gender')
        s.answer_time = end_time - start_time
        s.education = self.request.get('education')

        latex = self.request.get('latex')
        if latex == "yes":
            s.latex = True
        else:
            s.latex = False

        programming = self.request.get('programming')
        if programming == "yes":
            s.programming = True
        else:
            s.programming = False

        self.response.write("Thank you for your answer, you spend %d seconds on it!\n" % answer_time)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/answer', Answer)
])
