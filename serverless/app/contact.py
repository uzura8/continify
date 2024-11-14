import os
import json
from botocore.exceptions import ClientError
from flask import current_app, Blueprint, jsonify, request, render_template
from app.common.log import init_logger
from app.models.dynamodb import Contact, Service, ModelInvalidParamsException
from app.common.email import send_email_on_ses
from app.common.date import utc_str2local_str
from app.common.error import InvalidUsage
from app.common.string import random_str
from app.config_loader import load_config
from app.common.request import validate_params
from app.validators import NormalizerUtils
from app.common.recaptcha import verify_recaptcha

logger = init_logger()

bp = Blueprint('contact', __name__, url_prefix='/contacts')

PRJ_PREFIX = os.environ['PRJ_PREFIX']
SES_REGION = os.environ.get('SES_REGION')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')


@ bp.post('/<string:service_id>')
def post_contact(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    config_path = f'contact/{service_id}/config.yml'
    config = load_config(config_path)

    mail_config = config['mail']
    custom_fields = config.get('fields', {})

    optional_schemas = get_optional_schemas(custom_fields)
    schema = post_schema() | optional_schemas
    req_vals = validate_params(schema, request.json)

    if current_app.config['RECAPTCHA_ENABLED']:
        if not req_vals.get('recaptcha'):
            raise InvalidUsage('Recaptcha is required',
                               400, {'recaptcha': 'Recaptcha is required'})
        secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
        success, score, _ = verify_recaptcha(
            req_vals['recaptcha'], secret_key)
        # if action != 'contact':
        #     raise InvalidUsage('Recaptcha action is invalid', 400)
        if not success or score < 0.5:
            raise InvalidUsage('Recaptcha verification failed', 400)

    save_vals = convert_to_save(
        service_id, req_vals, custom_fields, mail_config)

    try:
        res = Contact.create(save_vals)
        save_res = Contact.to_response(res)
    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)
    except Exception as e:
        logger.exception(e)
        raise InvalidUsage('Server Error', 500)

    mail_vars = set_mail_vars(
        save_res['code'], save_res['createdAt'], config, req_vals)
    template_path = 'contact/{}/template.txt'.format(service_id)

    try:
        send_contact_email(mail_config, template_path, mail_vars)
    except Exception:
        raise InvalidUsage('Server Error', 500)

    return jsonify(save_res), 200


def set_mail_vars(code, created_at, config, vals):
    mail_config = config['mail']
    timezone = config.get('defaultTimezone', 'Asia/Tokyo')

    res = {} | vals
    res['code'] = code
    res['createdAtFormatted'] = utc_str2local_str(
        created_at, timezone, '%Y/%m/%d %H:%M')

    custom_fields = config.get('fields', {})
    if custom_fields:
        for key, val in custom_fields.items():
            if val['type'] == 'select':
                label_key = f'{key}Label'
                value_label = next(
                    (i['label'] for i in val['options'] if i['val'] == vals.get(key, '')), '')
                res[label_key] = value_label
    return res


def create_code(service_id):
    code = None
    service_id_code = None
    useable_code = None
    loop_count = 0
    loop_max = 5
    while useable_code is None:
        code = random_str(6, True)
        service_id_code = '#'.join([service_id, code])
        item = Contact.get_one(
            {'p': {'key': 'serviceIdCode', 'val': service_id_code}})
        if not item:
            useable_code = code

        loop_count += 1
        if loop_count > loop_max:
            raise InvalidUsage('Create code error', 404)

    return code, service_id_code


def send_contact_email(config, template_path, inputs):
    email_from = config['emailFrom']['address']
    email_to = inputs['email']

    try:
        res = send_email_on_ses(
            config['subject'],
            sender=(config['emailFrom']['name'], email_from),
            recipients=[email_to, email_from],
            text_body=render_template(
                template_path,
                email_to=email_to,
                inputs=inputs,
            ),
            region=SES_REGION
        )
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(
            f"SES ClientError: {error_code}, Message: {e.response['Error']['Message']}")
        raise e
    except Exception as e:
        logger.exception("Unexpected error occurred while sending email.")
        raise e

    return res


def convert_to_save(service_id, vals, custom_fields, email_info):
    save_vals = {
        'serviceId': service_id,
        'status': 0,
        'name': vals.get('name'),
        'email': vals.get('email'),
        'content': vals.get('content'),
    }
    items = create_code(service_id)
    save_vals['code'] = items[0]
    save_vals['serviceIdCode'] = items[1]

    custom_keys = custom_fields.keys()
    save_vals['customFields'] = {k: vals.get(k, '') for k in custom_keys}

    save_vals['emailInfo'] = email_info
    save_vals['requestInfo'] = {
        'ua': request.headers.get('User-Agent', ''),
        'ip': request.remote_addr,
    }
    return save_vals


def get_optional_schemas(fields):
    schemas = {}
    for key, item in fields.items():
        required = item.get('required', False)
        schemas[key] = {
            'required': required,
            'empty': True if not required else False,
            'nullable': True if not required else False,
        }
        if item['type'] == 'string':
            schemas[key]['type'] = 'string'
            schemas[key]['coerce'] = (NormalizerUtils.trim)
        elif item['type'] == 'select':
            schemas[key]['type'] = 'integer'
            schemas[key]['allowed'] = [i['val'] for i in item['options']]
        elif item['type'] == 'tel':
            schemas[key]['type'] = 'string'
            schemas[key]['coerce'] = (NormalizerUtils.trim)
            schemas[key]['valid_tel'] = True
        elif item['type'] == 'date':
            schemas[key]['type'] = 'string'
            schemas[key]['coerce'] = (NormalizerUtils.trim)
            schemas[key]['valid_date_str'] = True

    return schemas


def post_schema():
    return {
        'name': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'nullable': False,
        },
        # 'namePhonetic': {
        #     'type': 'string',
        #     'coerce': (NormalizerUtils.trim),
        #     'required': True,
        #     'empty': False,
        #     'nullable': False,
        # },
        'email': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'nullable': False,
            'valid_email': True,
        },
        # 'tel': {
        #     'type': 'string',
        #     'coerce': (NormalizerUtils.trim),
        #     'required': True,
        #     'empty': False,
        #     'nullable': False,
        #     'valid_tel': True,
        # },
        'content': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': True,
            'nullable': False,
            'empty': False,
            'default': '',
        },
        'recaptcha': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
        },
    }
