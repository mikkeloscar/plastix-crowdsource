import os
import time

from google.appengine.ext import db

import jinja2
import webapp2

nations = ["afghan", "albanian", "algerian", "american", "andorran", "angolan", "antiguans", "argentinean", "armenian", "australian", "austrian", "azerbaijani", "bahamian", "bahraini", "bangladeshi", "barbadian", "barbudans", "batswana", "belarusian", "belgian", "belizean", "beninese", "bhutanese", "bolivian", "bosnian", "brazilian", "british", "bruneian", "bulgarian", "burkinabe", "burmese", "burundian", "cambodian", "cameroonian", "canadian", "cape verdean", "central african", "chadian", "chilean", "chinese", "colombian", "comoran", "congolese", "costa rican", "croatian", "cuban", "cypriot", "czech", "danish", "djibouti", "dominican", "dutch", "east timorese", "ecuadorean", "egyptian", "emirian", "equatorial guinean", "eritrean", "estonian", "ethiopian", "fijian", "filipino", "finnish", "french", "gabonese", "gambian", "georgian", "german", "ghanaian", "greek", "grenadian", "guatemalan", "guinea-bissauan", "guinean", "guyanese", "haitian", "herzegovinian", "honduran", "british", "hungarian", "icelander", "indian", "indonesian", "iranian", "iraqi", "irish", "israeli", "italian", "ivorian", "jamaican", "japanese", "jordanian", "kazakhstani", "kenyan", "kittian and nevisian", "kuwaiti", "kyrgyz", "laotian", "latvian", "lebanese", "liberian", "libyan", "liechtensteiner", "lithuanian", "luxembourger", "macedonian", "malagasy", "malawian", "malaysian", "maldivan", "malian", "maltese", "marshallese", "mauritanian", "mauritian", "mexican", "micronesian", "moldovan", "monacan", "mongolian", "moroccan", "mosotho", "motswana", "mozambican", "namibian", "nauruan", "nepalese", "new zealander", "ni-vanuatu", "nicaraguan", "nigerien", "north korean", "northern irish", "norwegian", "omani", "pakistani", "palauan", "panamanian", "papua new guinean", "paraguayan", "peruvian", "polish", "portuguese", "qatari", "romanian", "russian", "rwandan", "saint lucian", "salvadoran", "samoan", "san marinese", "sao tomean", "saudi", "scottish", "senegalese", "serbian", "seychellois", "sierra leonean", "singaporean", "slovakian", "slovenian", "solomon islander", "somali", "south african", "south korean", "spanish", "sri lankan", "sudanese", "surinamer", "swazi", "swedish", "swiss", "syrian", "taiwanese", "tajik", "tanzanian", "thai", "togolese", "tongan", "trinidadian or tobagonian", "tunisian", "turkish", "tuvaluan", "ugandan", "ukrainian", "uruguayan", "uzbekistani", "venezuelan", "vietnamese", "welsh", "yemenite", "zambian", "zimbabwean"]

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
            'referer': referer,
            'nations': nations
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
