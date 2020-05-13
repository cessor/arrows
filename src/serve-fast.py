import logging
import os

# Set abspath to local
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options
from tornado.web import Application, url, StaticFileHandler

from config import environment, config_file

import web
import model

from motor import MotorClient

def initialize(connection_string):
    database = MotorClient(connection_string).greenarrow

    # Repository for Participants
    participants = model.Participants(database)
    routes = [
        url(r'/?', web.Home, dict(participants=participants)),
#        url(r'/new$', web.New, dict(participants=participants)),
        url(r'/api/trials/?$', web.Trials),
        url(r'/api/data/?$', web.Dropzone, dict(participants=participants)),
        url(r'/supervisor/?$', web.Supervisor, dict(participants=participants)),
        url(r'/supervisor/update/([a-f0-9]+)$', web.UpdateParticipant, dict(participants=participants)),
        url(r'/supervisor/login$', web.Login),
        url(r'/supervisor/logout$', web.Logout),
        url(r'/supervisor/xlsx/([a-f0-9]*)$', web.Xlsx, dict(participants=participants)),
        url(r'/reset$', web.Reset, dict(participants=participants)),
    ]
    return routes

def main():
    options.parse_config_file(config_file, final=False)
    options.parse_command_line()

    settings = dict(
        compress_response=True,
        cookie_secret=options.cookie_secret,
        debug=options.debug,
        login_url=options.login_url,
        static_path='static/',
        template_path='static/',
        xheaders=True,
    )

    routes = initialize(options.database)
    application = Application(routes, **settings)
    server = HTTPServer(application, xheaders=True)
    server.bind(options.port)
    server.start(1)  # Forks multiple sub-processes
    logging.info('Configured for "%s"' % environment)
    logging.info('Running on port %s' % options.port)
    IOLoop.current().start()

if __name__ == '__main__':
    main()
