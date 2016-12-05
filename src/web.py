import datetime
import json
import logging
import os

from tornado import gen
from tornado.concurrent import return_future
from tornado.web import RequestHandler, authenticated

import sampler
from model import Participant
from excel import ParticipantWorkbook, CompleteWorkbook


ADMIN_ID = 'ADMIN_ID'


def fastauth(fn):
    return authenticated(gen.coroutine(fn))


class Authenticated(RequestHandler):
    MUST_BE_ADMIN = False
    def get_current_user(self):
        if self.MUST_BE_ADMIN:
            return self.get_secure_cookie(ADMIN_ID)
        return self.get_secure_cookie(Participant.KEY)


class Admin(Authenticated):
    MUST_BE_ADMIN = True


class Home(Authenticated):
    def initialize(self, participants):
        self.participants = participants

    def _ip(self):
        '''Use for later identification of WHERE the study was ran'''
        x_real_ip = self.request.headers.get("X-Real-IP")
        remote_ip = x_real_ip or self.request.remote_ip
        return remote_ip

    @gen.coroutine
    def get(self):
        if not self.get_secure_cookie(Participant.KEY):
            self.redirect('/reset')
            return
        self.render("index.html")

# API:
#####

class Dropzone(Authenticated):
    def prepare(self):
        try:
            content_type = self.request.headers.get("Content-Type", '')
            if content_type and content_type.startswith("application/json"):
                json_args = json.loads(self.request.body.decode('utf-8'))
                self.json = json_args.get('data', {})
        except Exception as e:
            print(e)

    def initialize(self, participants):
        self.json = {}
        self.participants = participants

    @gen.coroutine
    def post(self):
        participant_id = self.get_current_user().decode('utf-8')
        if participant_id:
            data = self.json
            result = yield self.participants.add_trials(participant_id, data)
            try:
                # This was hacked into the system, because I wans't given any time to talk to the experimenters
                # if data is uploaded to the server, it checks if the set contains a VPN event
                # if so, the TAG is updated.
                # This is pokemon-Exceptionhandeled, so that it doesnt break
                VPN_CODE_EVENT_ID = 1021
                vpn_code_record = [record for record in data if record.get('event') == VPN_CODE_EVENT_ID][0]
                print(vpn_code_record)
                participant_code = vpn_code_record.get('data', participant_id)
                result = yield self.participants.update_tag(participant_id, participant_code)
            except Exception as e:
                print(e)

            self.finish({})
        else:
            self.clear()
            self.set_status(400)
            self.finish()


class Trials(Authenticated):
    def _prepare_response(self):
        self.set_header("Content-Type", "application/json")

    @gen.coroutine
    def get(self):
        block = sampler.Block().block
        self.finish(block)


class Reset(RequestHandler):
    def initialize(self, participants):
        self.participants = participants

    @gen.coroutine
    def get(self):
        participant = Participant()
        result = yield self.participants.create(participant)
        self.set_secure_cookie(Participant.KEY, participant.session_id)
        logging.info('[Session] New user created %s' % participant.session_id)
        self.redirect('/')


# Supervisor
############


class Login(RequestHandler):
    @gen.coroutine
    def get(self):
        self.render("login.html")

    @gen.coroutine
    def post(self):
        with open('.secret') as file_:
            secret = file_.read().strip()
        if self.get_argument('password') == secret:
            self.set_secure_cookie(ADMIN_ID, ADMIN_ID);
            self.redirect("/supervisor/")
        else:
            self.redirect("/")


class Logout(RequestHandler):
    @gen.coroutine
    def get(self):
        self.clear_cookie(ADMIN_ID)
        self.redirect("/")


def print_date(date):
    # MongoDb knows utc. When displaying, I want to be Local Time (gmt+1),
    # So I'm adding time to the received date to display the correct result
    date = date + datetime.timedelta(hours=2)
    return datetime.datetime.strftime(date, '%H:%M:%S on %b, %d.%m.%Y')

from decimal import Decimal
def calculate_payment(participant):
    a = participant.get('correct_trials')
    b = participant.get('incorrect_trials')

    a = Decimal(a)
    b = Decimal(b)
    factor = Decimal('0.05')
    return round((a - b) * factor, 2)

# I know, this should live somewhere else...
def prepare(dictionary):

    # Shift nested _id field up
    # This exists because of mongodb's mapreduce
    nested_id = dictionary.get('_id')
    del dictionary['_id']
    dictionary.update(nested_id)

    # Extract the timestamp from mongo's object id
    time = dictionary.get('_id').generation_time
    dictionary['date'] = print_date(time)


    # # Rename value to something meaningful

    values = dictionary.get('value')


    #
    if isinstance(values, dict):
        values = { key:int(value) for key,value in dictionary.get('value').items() }
        dictionary.update(values)
        payment =  calculate_payment(values)
        dictionary['payment'] = payment
    else:
        dictionary.update(dict(
            correct_trials= 0,
            incorrect_trials= 0,
            total_trials= 1,
            payment=0
        ))
    return dictionary


class Supervisor(Admin):
    def initialize(self, participants):
        self.participants = participants

    @fastauth
    def get(self):
        all_ = yield self.participants.all()
        participants = [prepare(data) for data in all_ if data]
        self.render('supervisor.html', participants=participants)


class UpdateParticipant(Admin):
    def prepare(self):
        try:
            content_type = self.request.headers.get("Content-Type", '')
            if content_type and content_type.startswith("application/json"):
                json_args = json.loads(self.request.body.decode('utf-8'))
                self.json = json_args.get('data', {})
        except Exception as e:
            print(e)

    def initialize(self, participants):
        self.participants = participants

    @fastauth
    def put(self, id_):
        tag = self.json.get('tag')
        if tag:
            print(tag)
            result = yield self.participants.update_tag(id_, tag)
        self.finish({})


@return_future
def make_participant_workbook(participant, callback):
    filename = ParticipantWorkbook(participant).write()
    callback(filename)


@return_future
def make_complete_workbook(events, callback):
    filename = CompleteWorkbook(events).write()
    callback(filename)


class Xlsx(Admin):
    def initialize(self, participants):
        self.participants = participants

    @fastauth
    def get(self, id_):
        if not id_:
            participants = yield self.participants.get_all_events().to_list(None)
            workbook_file_path = yield make_complete_workbook(participants)

        else:
            participant = yield self.participants.one(id_)
            if not participant:
                self.clear()
                self.set_status(404)
                self.finish()
                return
            else:
                workbook_file_path = yield make_participant_workbook(participant)

        assert workbook_file_path

        _, workbook_file_name = os.path.split(workbook_file_path)
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + workbook_file_name)

        # Read in file and write to output
        BUFFER_SIZE = 4096
        with open(workbook_file_path, 'rb') as file_:
            while True:
                data = file_.read(BUFFER_SIZE)
                if not data: break
                self.write(data)
        self.finish()
