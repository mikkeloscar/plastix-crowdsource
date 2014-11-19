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

NUM_EXERCISES = 20

def parse_exercises(fpath):
    fpath = os.path.join(os.path.split(__file__)[0], fpath)
    lines = []
    exercises = {}
    with open(fpath, "r") as f:
        lines = f.readlines()

    # remove first line holding headers
    lines.pop(0)

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
            exercises[elem[0]] = type_1
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
            choice_map = {
                    1: "v",
                    2: "x",
                    3: "y",
                    4: "z"
                    }
            for i, c in enumerate(elem[6:]):
                if c != "" and c != "\n":
                    choice = {
                            'img': c,
                            'value': i + 1,
                            'id': choice_map[i+1]
                            }
                    choices.append(choice)
            exercise['choices'] = choices
            if elem[1] == "2" or elem[1] == "3":
                exercises[elem[0]] = exercise
    return exercises

EXERCISES = parse_exercises('exercises/exercises.csv')

def generate_exercise_list(exercises):
    ex_shuffle = []
    ex_list = []
    ex_elems = []

    # produce a list we can shuffle later on
    for key, val in exercises.iteritems():
        ex_shuffle.append(val)

    random.shuffle(ex_shuffle)
    for i, s in enumerate(ex_shuffle):
        if i >= NUM_EXERCISES:
            break
        if s['id'] not in ex_list and s['element'] not in ex_elems:
            ex_list.append(s['id'])
            ex_elems.append(s['element'])
    return ex_list

def parse_history(history):
    if history == "":
        return [], []
    hist = history.split(';')
    ids = []
    elems = []
    for h in hist:
        s = h.split(':')
        ids.append(s[0])
        elems.append(s[1])
    return ids, elems

def get_exercise(history, num):
    exercise = None
    hist_ids, hist_elems = parse_history(history)
    shuffle = list(EXERCISES[1] + EXERCISES[2] + EXERCISES[3])
    random.shuffle(shuffle)
    for s in shuffle:
        if s['id'] not in hist_ids and s['element'] not in hist_elems:
            exercise = s
            break
    if not exercise:
        return "", False
    if history == "":
        history = []
    else:
        history = history.split(';')
    history.append(exercise['id'] + ':' + exercise['element'])
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
    easy = db.StringProperty()
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
    feedback = db.TextProperty(indexed=False)


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
        }

        view = JINJA_ENVIRONMENT.get_template('welcome.html')
        self.response.write(view.render(values))

    def post(self):
        start_time = int(self.request.get('start_time'))
        ref = self.request.get('referer')
        ref_id = self.request.get('ref_id')

        values = {
            'start_time': start_time,
            'referer': ref,
            'ref_id': ref_id,
            'nations': nations,
        }

        view = JINJA_ENVIRONMENT.get_template('survey.html')
        self.response.write(view.render(values))



class Start(webapp2.RequestHandler):

    # def get(self):
    #     # collect some userdata
    #     referer = self.request.referer
    #     start_time = int(time.time()) # now unix time
    #     ref_id = self.request.get('r')

    #     values = {
    #         'start_time': start_time,
    #         'referer': referer,
    #         'ref_id': ref_id,
    #         'nations': nations,
    #     }

    #     view = JINJA_ENVIRONMENT.get_template('survey.html')
    #     self.response.write(view.render(values))

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

        self.redirect('/exercise/1?id=%d#no-back' % s.key().id())


class Exercise(webapp2.RequestHandler):

    def get(self, num):

        nums = 0
        if self.request.cookies.get('nums'):
            nums = int(self.request.cookies.get('nums'))

        if num == "1" and not self.request.cookies.get('exercises'):
            # generate exercises list
            exercises = generate_exercise_list(EXERCISES)

            survey_id = self.request.get('id')

            self.response.set_cookie("survey_id", str(survey_id), overwrite=True)
            self.response.set_cookie("nums", str(len(exercises)), overwrite=True)
            self.response.set_cookie("exercises", ';'.join(exercises),
                    overwrite=True)

        elif int(num) <= nums:
            exercises = self.request.cookies.get('exercises').split(';')
        else:
            self.response.write('Invalid request')
            self.response.set_status(404)

        ex_num = exercises[int(num)-1]

        exercise = EXERCISES[ex_num]

        # suffle choices
        if exercise['type'] in ["2", "3"]:
            random.shuffle(exercise['choices'])

        values = {
                # 'history': history,
                'type': exercise['type'],
                'ex_id': exercise['id'],
                'exercise': exercise,
                'submit': 'Continue'
                }
        if int(num) == nums:
            values['submit'] = 'Submit'

        view = JINJA_ENVIRONMENT.get_template('exercise.html')
        self.response.write(view.render(values))


    def post(self, num):
        survey_id = self.request.cookies.get('survey_id')
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

        if int(num) < int(self.request.cookies.get('nums')):
            self.redirect('/exercise/%d' % (int(num) + 1))
        else:
            # get SurveyModel and add answer_time and endtime
            s = SurveyModel.get_by_id(int(survey_id))
            s.end_time = int(time.time()) # now unix time
            s.answer_time = s.end_time - s.start_time
            try:
                s.put()
            except Exception as e:
                self.response.write('{0}'.format(e))

            values = {
                    'survey_id': survey_id,
                    'feedback': False
                    }
            view = JINJA_ENVIRONMENT.get_template('finish.html')
            self.response.write(view.render(values))


class Finish(webapp2.RequestHandler):

    def post(self):
        survey_id = self.request.get('survey_id')
        # get SurveyModel and add feedback
        s = SurveyModel.get_by_id(int(survey_id))
        s.feedback = self.request.get('feedback')
        try:
            s.put()
        except Exception as e:
            self.response.write('{0}'.format(e))

        values = {
                'survey_id': survey_id,
                'feedback': True
                }
        view = JINJA_ENVIRONMENT.get_template('finish.html')
        self.response.write(view.render(values))

class Data(webapp2.RequestHandler):

    def get(self, t):
        if t == "exercises":
            exercises = ExerciseModel.all()
            output = []
            output.append(exercise_csv_header())
            for e in exercises:
                output.append(exercise_to_csv(e))
            self.response.write("\n".join(output))
        elif t == "surveys":
            surveys = SurveyModel.all()
            output = []
            output.append(survey_csv_header())
            for s in surveys:
                output.append(survey_to_csv(s))
            self.response.write("\n".join(output))
        else:
            self.response.write("nothing\n")

def exercise_csv_header():
    return ','.join([
        wrap("Survey ID"),
        wrap("Exercise Type"),
        wrap("Exercise ID"),
        wrap("Choice"),
        wrap("Answer"),
        wrap("More"),
        wrap("Answer (Easy question)"),
        wrap("Date")
        ])

def exercise_to_csv(e):
    return ','.join([
        str(e.survey_id),
        str(e.ex_type),
        str(e.ex_id),
        str(e.choice),
        wrap(e.answer),
        wrap(e.more),
        wrap(e.easy),
        str(e.date)
        ])

def survey_csv_header():
    return ','.join([
        wrap("ID"),
        wrap("Date"),
        wrap("referer"),
        wrap("referer ID"),
        wrap("IP"),
        wrap("Age"),
        wrap("Gender"),
        wrap("Nationality"),
        wrap("Start time (UNIX)"),
        wrap("Answer time (Seconds)"),
        wrap("End time (UNIX)"),
        wrap("Education"),
        wrap("Field"),
        wrap("Programming experience"),
        wrap("Programming proficiency level"),
        wrap("Programming languages"),
        wrap("Feedback")
        ])


def survey_to_csv(s):
    return ','.join([
        str(s.key().id()),
        str(s.date),
        wrap(s.ref),
        wrap(s.ref_id),
        wrap(s.ip),
        str(s.age),
        wrap(s.gender),
        wrap(s.nation),
        str(s.start_time),
        str(s.answer_time),
        str(s.end_time),
        str(s.education),
        wrap(s.field),
        str(s.programming),
        str(s.programmingex),
        str(s.programminglang),
        wrap(s.feedback),
        ])

def wrap(field):
    if field and isinstance(field, unicode):
        field = field.encode('utf8')
    return '"%s"' % str(field).replace("\"", "\\\"")


app = webapp2.WSGIApplication([
    ('/', Index),
    ('/start', Start),
    (r'/exercise/(\d+)', Exercise),
    ('/finish', Finish),
    (r'/csv/(\w+)', Data),
])
