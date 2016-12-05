from tornado import gen
from tornado.web import RequestHandler
from web import Authenticated

import json
import logging
import sampler


class Block(Authenticated):
    def initialize(self, sessions):
        self.sessions = sessions

    def _prepare_response(self):
        self.set_header("Content-Type", "application/json")

    @gen.coroutine
    def get(self):
        block = sampler.Block().block
        self.finish(block)


class Dropzone(Authenticated):
    def prepare(self):
        try:
            content_type = self.request.headers.get("Content-Type", '')
            if content_type and content_type.startswith("application/json"):
                json_args = json.loads(self.request.body.decode('utf-8'))
                self.json = json_args.get('data', {})
        except Exception as e:
            print(e)

    def initialize(self, sessions):
        self.json = {}
        self.sessions = sessions

    @gen.coroutine
    def post(self):
        current_user = self.get_current_user()
        if current_user:
            data = self.json
            result = yield self.sessions.add_trials(current_user, data)
            self.finish({})
        else:
            self.clear()
            self.set_status(400)
            self.finish()