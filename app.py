import os
import time
import random

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

NUM_EXERCISES = 5

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
    if len(elem) >= 5:
        if elem[1] == "1":
            type_1 = {
                    'id': elem[0],
                    'type': elem[1],
                    'element': elem[2],
                    'easy': elem[3],
                    'text': elem[4],
                    'img': elem[5]
                    }
            exercises[1].append(type_1)
        else:
            exercise = {
                    'id': elem[0],
                    'type': elem[1],
                    'element': elem[2],
                    'easy': elem[3],
                    'text': elem[4],
                    'img': elem[5]
                    }
            choices = []
            for i, c in enumerate(elem[6:]):
                if c != "":
                    choice = {
                            'img': c,
                            'value': i + 1
                            }
                    choices.append(choice)
            exercise['choices'] = choices
            if elem[1] == "2":
                exercises[2].append(exercise)
            else:
                exercises[3].append(exercise)
    return exercises

EXERCISES = parse_exercises('exercises/exercises.csv')

def get_exercise(history, num):
    exercise = None
    history = history.split(';')
    if num <= NUM_EXERCISES / 3:
        # show type 1 exercises first in the survey
        shuffle = list(EXERCISES[1])
    else:
        shuffle = list(EXERCISES[2] + EXERCISES[3])
    random.shuffle(shuffle)
    for s in shuffle:
        if s not in history:
            exercise = s
            break
    history.append(exercise['id'])
    history = ';'.join(history)
    if exercise['type'] in ["2", "3"]:
        random.shuffle(exercise['choices'])
    return history, exercise


class ExerciseModel(db.Model):
    survey_id = db.IntegerProperty()
    ex_type = db.IntegerProperty()
    ex_id = db.IntegerProperty()
    choice = db.IntegerProperty()
    answer = db.TextProperty(indexed=False)
    more = db.TextProperty(indexed=False)
    more = db.StringProperty()
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

        history, exercise = get_exercise("", 1)

        values = {
                'survey_id': survey_id,
                'type': exercise['type'],
                'history': history,
                'ex_id': exercise['id'],
                'num': 1,
                'exercise': exercise,
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
            try:
                e.choice = int(self.request.get('choice'))
            except ValueError:
                e.choice = 0
        elif e.ex_type == 1:
            e.answer = self.request.get('answer')

        e.more = self.request.get('more')
        e.easy = self.request.get('easy')

        try:
            e.put()
        except Exception as e:
            self.response.write('{0}'.format(e))

        # prepare for new exercise
        if int(num) <= NUM_EXERCISES:
            new_num = int(num) + 1
            # generate random exercise
            history, exercise = get_exercise("", new_num)
            values = {
                    'survey_id': survey_id,
                    'type': exercise['type'],
                    'history': history,
                    'ex_id': exercise['id'],
                    'num': new_num,
                    'exercise': exercise
                    }
            if int(num) == NUM_EXERCISES:
                values['submit'] = 'Submit'
            else:
                values['submit'] = 'Continue'

            view = JINJA_ENVIRONMENT.get_template('exercise.html')
            self.response.write(view.render(values))
        else:
            # get SurveyModel and add answer_time and endtime
            s = SurveyModel.get_by_id(int(survey_id))
            s.end_time = int(time.time()) # now unix time
            s.answer_time = s.end_time - s.start_time
            try:
                s.put()
            except Exception as e:
                self.response.write('{0}'.format(e))
            self.response.write("Thank you for your answers, you spend %d seconds on them!\n" % s.answer_time)


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/exercise', Exercise),
    (r'/exercise/(\d+)', Exercise)
])
