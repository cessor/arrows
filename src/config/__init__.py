import os
from tornado.options import define, options
environment = os.environ.get('TORNADO_ENV', 'local').strip()
config_file = os.path.join('config', "%s.cfg" % environment)

#define('port', default=5000, callback= lambda path: options.parse_command_line())
define('autoreload', default=False)
define('cookie_secret')
define('database')
define('debug', default=False)
define('login_url', default='/login')
define('port', default=5000)
define('study_tag', 'test')
define('xsrf_cookies', default=True)