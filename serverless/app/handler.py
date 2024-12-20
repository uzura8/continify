import os
import logging
from flask import Flask, jsonify, request
from flask_cognito import CognitoAuth
from werkzeug.routing import Rule
from app.common.log import get_log_level_by_env
from app.common.error import InvalidUsage
from app.common.custom_json_provider import CustomJsonProvider
from app.root import bp as root_module
from app.vote import bp as vote_module
from app.post import bp as post_module
from app.comment import bp as comment_module
from app.category import bp as category_module
from app.tag import bp as tag_module
from app.admin import bp as admin_module
from app.contact import bp as contact_module


cors_accept_origins_str = os.environ.get('CORS_ACCEPT_ORIGINS', '')
CORS_ACCEPT_ORIGINS = cors_accept_origins_str.split(
    ',') if cors_accept_origins_str else []


app = Flask(
    __name__,
    template_folder='../config')
app.url_map.strict_slashes = False
app.json = CustomJsonProvider(app)

jinja_options = app.jinja_options.copy()
jinja_options.update({
    'block_start_string': '[%',
    'block_end_string': '%]',
    'variable_start_string': '[[',
    'variable_end_string': ']]',
    'comment_start_string': '[#',
    'comment_end_string': '#]'
})
app.jinja_options = jinja_options

# set logger
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - [module: %(module)s line: %(lineno)d] - %(message)s'
)
stdout_handler = logging.StreamHandler()
stdout_handler.setFormatter(formatter)
app.logger.addHandler(stdout_handler)
log_level = get_log_level_by_env()
app.logger.setLevel(log_level)

app.config.update({
    'COGNITO_REGION': os.environ.get('COGNITO_REGION', ''),
    'COGNITO_USERPOOL_ID': os.environ.get('COGNITO_USERPOOL_ID', ''),
    'COGNITO_APP_CLIENT_ID': os.environ.get('COGNITO_APP_CLIENT_ID', ''),
    'COGNITO_CHECK_TOKEN_EXPIRATION': os.environ.get('COGNITO_CHECK_TOKEN_EXPIRATION', True),
    'COGNITO_JWT_HEADER_NAME': os.environ.get('COGNITO_JWT_HEADER_NAME', 'Authorization'),
    'COGNITO_JWT_HEADER_PREFIX': os.environ.get('COGNITO_JWT_HEADER_PREFIX', 'Bearer'),
})
cogauth = CognitoAuth(app)

RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
RECAPTCHA_ENABLED = bool(RECAPTCHA_SITE_KEY and RECAPTCHA_SECRET_KEY)
app.config.update({
    'RECAPTCHA_ENABLED': RECAPTCHA_ENABLED,
    'RECAPTCHA_SITE_KEY': RECAPTCHA_SITE_KEY,
    'RECAPTCHA_SECRET_KEY': RECAPTCHA_SECRET_KEY,
})

# get prefix from environment variable
APP_ROOT = os.getenv('APP_ROOT')
if not APP_ROOT is None:
    # define custom_rule class
    class Custom_Rule(Rule):
        def __init__(self, string, *args, **kwargs):
            # check endswith '/'
            if APP_ROOT.endswith('/'):
                prefix_without_end_slash = APP_ROOT.rstrip('/')
            else:
                prefix_without_end_slash = APP_ROOT
            # check startswith '/'
            if APP_ROOT.startswith('/'):
                prefix = prefix_without_end_slash
            else:
                prefix = '/' + prefix_without_end_slash
            super().__init__(prefix + string, *args, **kwargs)

    # set url_rule_class
    app.url_rule_class = Custom_Rule


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.after_request
def add_cors_headers(response):
    response.headers.add('X-Content-Type-Options', 'nosniff')

    r = request.referrer[:-1] if request.referrer else None
    if not CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', '*')

    elif r is not None and r in CORS_ACCEPT_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', r)

    if not CORS_ACCEPT_ORIGINS or r is not None and r in CORS_ACCEPT_ORIGINS:
        allow_headers = ['X-Requested-With', 'X-HTTP-Method-Override', 'Content-Type',
                         'Cache-Control', 'Accept', 'Authorization', 'Time-Zone']
        response.headers.add('Access-Control-Allow-Headers',
                             ','.join(allow_headers))
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, OPTIONS, PUT, DELETE')
        response.headers.add('Access-Control-Allow-Credentials', 'true')

    return response


app.register_blueprint(vote_module)
app.register_blueprint(category_module)
app.register_blueprint(tag_module)
app.register_blueprint(post_module)
app.register_blueprint(comment_module)
app.register_blueprint(admin_module)
app.register_blueprint(root_module)
app.register_blueprint(contact_module)
