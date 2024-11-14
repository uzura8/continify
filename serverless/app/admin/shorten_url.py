import json
import traceback
from urllib.parse import quote, urlparse
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import ShortenUrl, ShortenUrlDomain, ModelInvalidParamsException
from app.common.date import utc_iso
from app.common.error import InvalidUsage
from app.common.request import validate_req_params, validate_params
from app.common.log import init_logger
from app.validators import NormalizerUtils
from app.admin import bp, site_before_request, check_acl_service_id, admin_role_editor_required

PARAM_VAL_PREFIX = 'qr'

logger = init_logger()


def check_url_id(service_id, url_id):
    keys = {'urlId': url_id}
    validate_req_params(validation_schema_url_id(), keys)
    saved = ShortenUrl.get_one_by_pkey_new(keys, False, True)
    if not saved:
        raise InvalidUsage('UrlId does not exist', 404)
    if service_id != saved['serviceId']:
        raise InvalidUsage('ServiceId is invalid', 400)
    check_acl_service_id(saved['serviceId'])
    return saved


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.get('/shorten-urls/<string:service_id>')
@cognito_auth_required
@admin_role_editor_required
def get_url_list(service_id):
    check_acl_service_id(service_id)
    params = {}
    for key in ['count', 'order', 'status', 'url']:
        params[key] = request.args.get(key)
    vals = validate_params(validation_schema_url_list_get(), params)

    keys = {'serviceId': service_id}
    if vals.get('status'):
        keys['confirmStatusCreatedAt'] = vals['status']
        index = 'ServiceStatusIndex'
        skey_cond_type = 'begins_with'
    elif vals.get('url'):
        keys['urlCreatedAt'] = vals['url']
        index = 'ServiceUrlIndex'
        skey_cond_type = 'begins_with'
    else:
        index = 'createdAtGsi'
        skey_cond_type = 'eq'

    vals['index'] = index

    key_name = 'pagerKey'
    req_pager_key = request.args.get(key_name)
    if req_pager_key:
        params = {key_name: req_pager_key}
        pager_key = validate_params(get_pager_key_schema(index), params)
        vals = {**vals, **pager_key}

    res = ShortenUrl.get_all_pager_new(
        keys, vals, index, True, skey_cond_type)
    return jsonify(res), 200


@bp.post('/shorten-urls/<string:service_id>')
@cognito_auth_required
@admin_role_editor_required
def post_url(service_id):
    check_acl_service_id(service_id)
    schema = validation_schema_url_post()
    vals = validate_req_params(schema, request.json)
    vals['serviceId'] = service_id

    created_by = current_cognito_jwt.get('cognito:username', '')
    if created_by:
        vals['createdBy'] = created_by

    try:
        res = ShortenUrl.create_item(vals, PARAM_VAL_PREFIX)
    except ModelInvalidParamsException as e:
        logger.error(e.message, exc_info=True)
        raise InvalidUsage(e.message, 400)
    except Exception as e:
        logger.error(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    return jsonify(res), 200


@bp.route('/shorten-urls/<string:service_id>/<string:url_id>', methods=['GET', 'HEAD'])
@cognito_auth_required
@admin_role_editor_required
def get_url_detail(service_id, url_id):
    saved = check_url_id(service_id, url_id)
    if request.method == 'HEAD':
        return jsonify(), 200
    return jsonify(saved), 200


@bp.post('/shorten-urls/<string:service_id>/<string:url_id>')
@cognito_auth_required
@admin_role_editor_required
def post_url_detail(service_id, url_id):
    check_url_id(service_id, url_id)
    schema = validation_schema_url_post()
    vals = validate_req_params(schema, request.json)
    vals['serviceId'] = service_id
    vals['updatedBy'] = current_cognito_jwt.get('cognito:username', '')
    try:
        updated = ShortenUrl.update_item(url_id, vals, PARAM_VAL_PREFIX)
    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)
    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)
    return jsonify(updated), 200


@bp.delete('/shorten-urls/<string:service_id>/<string:url_id>')
@cognito_auth_required
@admin_role_editor_required
def delete_url_detail(service_id, url_id):
    saved = check_url_id(service_id, url_id)
    try:
        ShortenUrl.delete({'urlId': url_id})
        check_exists_in_urls_and_delete_domain(service_id, saved['domain'])

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    return jsonify(), 204


@bp.route('/shorten-urls/<string:service_id>/domains', methods=['GET'])
@cognito_auth_required
@admin_role_editor_required
def url_domain_list(service_id):
    check_acl_service_id(service_id)
    keys = {'p': {'key': 'serviceId', 'val': service_id}}
    domains = ShortenUrlDomain.get_all(keys, False, 'serviceIdIndex')
    return jsonify(domains), 200


def check_exists_in_urls_and_delete_domain(service_id, domain):
    # If old domain not exits in urls table, delete from domains table
    domain_key = f'{service_id}#{domain}'
    query_keys = {'p': {'key': 'serviceIdDomain', 'val': domain_key}}
    url_item = ShortenUrl.get_one(query_keys, False, 'serviceIdDomainIndex')
    if url_item:
        return

    try:
        ShortenUrlDomain.delete({'serviceIdDomain': domain_key})
    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)
    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)


def validation_schema_url_id():
    return {
        'urlId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 10,
            'regex': r'^[0-9a-zA-Z]{10}$',
        }
    }


def validation_schema_url_post():
    return {
        'url': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': True,
            'nullable': False,
            'empty': False,
            'valid_url': True,
        },
        'name': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'description': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'isViaJumpPage': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
        'isConfirmed': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': False,
            'default': False,
        },
        'assigneeName': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'assigneeMemo': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'paramKey': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
            'dependencies': 'paramValue',
        },
        'paramValue': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
            'dependencies': 'paramKey',
        },
    }


def validation_schema_url_list_get():
    return {
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 100,
            'default': 50,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
        },
        'status': {
            'type': 'string',
            'required': False,
            'empty': True,
            'nullable': True,
            'allowed': ShortenUrl.allowed_vals['confirmStatus'],
        },
        'url': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'nullable': True,
            'default': '',
        },
    }


def get_pager_key_schema(index):
    schema = {
        'type': 'dict',
        'coerce': (NormalizerUtils.json2dict),
        'required': False,
        'empty': True,
        'nullable': True,
        'schema': {
            'serviceId': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
            'urlId': {
                'type': 'string',
                'required': True,
                'empty': False,
            },
        }
    }
    if index == 'createdAtGsi':
        schema['schema']['createdAt'] = {
            'type': 'string',
            'required': True,
            'empty': False,
            'regex': r'\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
        }
    elif index == 'ServiceStatusIndex':
        schema['schema']['confirmStatusCreatedAt'] = {
            'type': 'string',
            'required': True,
            'empty': False,
        }
    elif index == 'ServiceUrlIndex':
        schema['schema']['urlCreatedAt'] = {
            'type': 'string',
            'required': True,
            'empty': False,
        }
    return {'pagerKey': schema}
