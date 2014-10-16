import os
import time

from google.appengine.ext import db

import jinja2
import webapp2

nations = ["afghan", "albanian", "algerian", "american", "andorran", "angolan",
"antiguans", "argentinean", "armenian", "australian", "austrian",
"azerbaijani", "bahamian", "bahraini", "bangladeshi", "barbadian", "barbudans",
"batswana", "belarusian", "belgian", "belizean", "beninese", "bhutanese",
"bolivian", "bosnian", "brazilian", "british", "bruneian", "bulgarian",
"burkinabe", "burmese", "burundian", "cambodian", "cameroonian", "canadian",
"cape verdean", "central african", "chadian", "chilean", "chinese",
"colombian", "comoran", "congolese", "costa rican", "croatian", "cuban",
"cypriot", "czech", "danish", "djibouti", "dominican", "dutch",
"east timorese", "ecuadorean", "egyptian", "emirian", "equatorial guinean",
"eritrean", "estonian", "ethiopian", "fijian", "filipino", "finnish", "french",
"gabonese", "gambian", "georgian", "german", "ghanaian", "greek", "grenadian",
"guatemalan", "guinea-bissauan", "guinean", "guyanese", "haitian",
"herzegovinian", "honduran", "british", "hungarian", "icelander", "indian",
"indonesian", "iranian", "iraqi", "irish", "israeli", "italian", "ivorian",
"jamaican", "japanese", "jordanian", "kazakhstani", "kenyan",
"kittian and nevisian", "kuwaiti", "kyrgyz", "laotian", "latvian", "lebanese",
"liberian", "libyan", "liechtensteiner", "lithuanian", "luxembourger",
"macedonian", "malagasy", "malawian", "malaysian", "maldivan", "malian",
"maltese", "marshallese", "mauritanian", "mauritian", "mexican", "micronesian",
"moldovan", "monacan", "mongolian", "moroccan", "mosotho", "motswana",
"mozambican", "namibian", "nauruan", "nepalese", "new zealander", "ni-vanuatu",
"nicaraguan", "nigerien", "north korean", "northern irish", "norwegian",
"omani", "pakistani", "palauan", "panamanian", "papua new guinean",
"paraguayan", "peruvian", "polish", "portuguese", "qatari", "romanian",
"russian", "rwandan", "saint lucian", "salvadoran", "samoan", "san marinese",
"sao tomean", "saudi", "scottish", "senegalese", "serbian", "seychellois",
"sierra leonean", "singaporean", "slovakian", "slovenian", "solomon islander",
"somali", "south african", "south korean", "spanish", "sri lankan", "sudanese",
"surinamer", "swazi", "swedish", "swiss", "syrian", "taiwanese", "tajik",
"tanzanian", "thai", "togolese", "tongan", "trinidadian or tobagonian",
"tunisian", "turkish", "tuvaluan", "ugandan", "ukrainian", "uruguayan",
"uzbekistani", "venezuelan", "vietnamese", "welsh", "yemenite", "zambian",
"zimbabwean"]

# jinja settings
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__),
        'views')),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

NUM_EXERCISES = 20

def parse_exercises(fpath):
    fpath = os.path.join(os.path.split(__file__)[0], fpath)
    lines = []
    exercises = {
            1: [],
            2: [],
            3: []
            }
    with open(fpath, "r") as f:
        lines = f.readlines()

    for line in lines:
        exercises = parse_line(line, exercises)
    return exercises


def parse_line(line, exercises):
    elem = line.split('\t')
    if elem[1] == "1":
        type_1 = {
                'id': elem[0],
                'element': elem[2],
                'text': elem[3],
                'img': elem[4]
                }
        exercises[1].append(type_1)
    elif elem[1] == "2":
        type_2 = {
                'id': elem[0],
                'element': elem[2],
                'text': elem[3],
                'choice1': elem[5],
                'choice2': elem[6],
                'choice2': elem[7],
                }
        exercises[2].append(type_2)
    elif elem[1] == "3":
        type_3 = {
                'id': elem[0],
                'element': elem[2],
                'text': elem[3],
                'choice1': elem[5],
                'choice2': elem[6],
                'choice2': elem[7],
                }
        exercises[3].append(type_3)
    return exercises

EXERCISES = parse_exercises('exercises/exercises.csv')

class ExerciseModel(db.Model):
    survey_id = db.IntegerProperty()
    ex_type = db.IntegerProperty()
    ex_id = db.IntegerProperty()
    choice = db.StringProperty(choices=set(["choice1", "choice2", "choice3"]))
    answer = db.TextProperty(indexed=False)
    date = db.DateTimeProperty(auto_now_add=True)

# DataStore
class SurveyModel(db.Model):
    date = db.DateTimeProperty(auto_now_add=True)
    ref = db.StringProperty() # HTTP_REFERER
    ref_id = db.StringProperty()
    ip = db.StringProperty() # users IP (used to prevent multiple entries)
    age = db.IntegerProperty()
    gender = db.StringProperty(choices=set(["male", "female"]))
    nation = db.StringProperty()
    start_time = db.IntegerProperty()
    answer_time = db.IntegerProperty() # time in seconds
    end_time = db.IntegerProperty()
    education = db.IntegerProperty() # education
    field = db.StringProperty() # field
    programming = db.BooleanProperty(indexed=False, default=False)
    programmingex = db.IntegerProperty()
    programminglang = db.StringProperty()


class Index(webapp2.RequestHandler):

    def get(self):
        # collect some userdata
        referer = self.request.referer
        start_time = int(time.time()) # now unix time
        ref_id = self.request.get('r')

        values = {
            'start_time': start_time,
            'referer': referer,
            'ref_id': ref_id,
            'nations': nations,
        }

        view = JINJA_ENVIRONMENT.get_template('survey.html')
        self.response.write(view.render(values))

    def post(self):
        start_time = int(self.request.get('start_time'))
        ref = self.request.get('referer')
        ref_id = self.request.get('ref_id')

        s = SurveyModel()
        s.start_time = start_time
        s.ref = ref
        s.ref_id = ref_id
        s.ip = self.request.remote_addr
        try:
            s.age = int(self.request.get('age'))
        except ValueError:
            s.age = 0
        s.gender = self.request.get('gender')
        s.nation = self.request.get('nation')
        try:
            s.education = int(self.request.get('education'))
        except ValueError:
            s.education = 0
        s.field = self.request.get('education2')
        programming = self.request.get('programming')
        if programming == "yes":
            s.programming = True
        else:
            s.programming = False
        try:
            s.programmingex = int(self.request.get('programmingex'))
        except ValueError:
            s.programmingex = 0
        l = ';'.join(self.request.get_all('programminglang'))
        s.programminglang = l

        # store in DB
        try:
            s.put()
        except Exception as e:
            self.response.write('{0}\n'.format(e)) # TODO fix
            return

        print(s.key().id())

        self.redirect('/exercise?id=%d' % s.key().id())


class Exercise(webapp2.RequestHandler):

    def get(self):
        survey_id = self.request.get('id')

        values = {
                'survey_id': survey_id,
                'type': 1,
                'history': '1',
                'ex_id': 2,
                'num': 1,
                'exercise': dict(),
                'submit': 'Continue'
                }

        view = JINJA_ENVIRONMENT.get_template('exercise.html')
        self.response.write(view.render(values))

    def post(self, num):
        survey_id = self.request.get('survey_id')

        # store exercise
        e = ExerciseModel()
        e.survey_id = int(survey_id)
        e.ex_type = int(self.request.get('type'))
        e.ex_id = int(self.request.get('ex_id'))
        if e.ex_type in [2,3]:
            choice = self.request.get('choice')
        elif e.ex_type == 1:
            answer = self.request.get('answer')

        try:
            e.put()
        except Exception as e:
            self.response.write('{0}'.format(e))

        # prepare for new exercise
        if int(num) <= NUM_EXERCISES:
            # TODO generate random exercise
            values = {
                    'survey_id': survey_id,
                    'type': 1,
                    'history': '1',
                    'ex_id': 2,
                    'num': int(num) + 1,
                    'exercise': dict()
                    }
            if int(num) == NUM_EXERCISES:
                values['submit'] = 'Submit'
            else:
                values['submit'] = 'Continue'

            view = JINJA_ENVIRONMENT.get_template('exercise.html')
            self.response.write(view.render(values))
        else:
            # TODO get SurveyModel and add answer_time and endtime
            self.response.write("Thank you for your answers, you spend %d seconds on them!\n" % answer_time)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/exercise', Exercise),
    (r'/exercise/(\d+)', Exercise)
])
