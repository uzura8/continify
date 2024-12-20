import traceback
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Service, ServiceConfig, ServiceContent, \
    Category, AdminUserConfig, Comment, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.request import validate_req_params, validate_params
from app.validators import NormalizerUtils
from app.validators.schemas.common import get_pager_list_schemas, content_id_schema
from app.admin import bp, site_before_request, admin_role_admin_required, \
    check_acl_service_id, admin_role_editor_required, check_admin_role


def get_service_content(service_id, content_id, raise_404=True):
    schema = {'contentId': content_id_schema}
    validate_params(schema, {'contentId': content_id})
    keys = {'serviceId': service_id, 'contentId': content_id}
    item = ServiceContent.get_one_by_pkey_new(keys, False, True)
    if raise_404 and not item:
        raise InvalidUsage('ServiceId does not exist', 404)
    return item


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.route('/services', methods=['POST', 'GET'])
@cognito_auth_required
@admin_role_admin_required
def service_list():
    services = Service.scan()
    services = sorted(services, key=lambda x: x['serviceId'])
    if request.method == 'POST':
        vals = validate_req_params(validation_schema_services(), request.json)
        if next((x for x in services if x['serviceId'] == vals['serviceId']), None):
            raise InvalidUsage('ServiceId already used', 400)

        configs = None
        if 'configs' in vals:
            configs = vals.pop('configs')

        service = Service.create(vals)

        if configs is not None and any(configs):
            for name, val in configs.items():
                ServiceConfig.save(service['serviceId'], name, val)

        service['configs'] = ServiceConfig.get_all_by_service(
            service['serviceId'], True, True, True)

        admin_username = current_cognito_jwt.get('cognito:username', '')
        if not admin_username:
            raise InvalidUsage('username is empty', 400)

        # Add serviceId to acceptServiceIds in admin user configs
        accepted_sids = AdminUserConfig.get_val(
            admin_username, 'acceptServiceIds')
        accepted_sids.append(service['serviceId'])
        AdminUserConfig.save(admin_username, 'acceptServiceIds', accepted_sids)

        # Create root category
        vals = {
            'serviceId': service['serviceId'],
            'parentId': 0,
            'slug': 'root',
            'label': 'ルート{}'.format(service['label']),
        }
        Category.create(vals)

        return jsonify(service), 200

    return jsonify(services), 200


@bp.route('/services/configs', methods=['GET'])
@cognito_auth_required
def service_configs():
    configs = ServiceConfig.get_alloweds()
    return jsonify(configs), 200


@bp.route('/services/<string:service_id>', methods=['POST', 'GET', 'HEAD'])
@cognito_auth_required
@admin_role_editor_required
def service_detail(service_id):
    if request.method == 'HEAD':
        service = Service.get_one(
            {'p': {'key': 'serviceId', 'val': service_id}})
        if service:
            return jsonify(), 200
        else:
            return jsonify(), 404

    service = check_acl_service_id(service_id)
    if not service:
        raise InvalidUsage('ServiceId does not exist', 404)

    if request.method == 'POST':
        check_admin_role('admin')

        alloweds = ['label', 'functions', 'configs']
        vals = validate_req_params(
            validation_schema_services(), request.json, alloweds)
        configs = None
        if 'configs' in vals:
            configs = vals.pop('configs')

        service = Service.update(
            {'p': {'key': 'serviceId', 'val': service_id}}, vals, True)

        if configs is not None and any(configs):
            for name, val in configs.items():
                ServiceConfig.save(service_id, name, val)

    service['configs'] = ServiceConfig.get_all_by_service(
        service_id, True, True, True)
    return jsonify(service), 200


@bp.get('/services/<string:service_id>/configs/<string:config_name>')
@cognito_auth_required
@admin_role_editor_required
def service_config_detail(service_id, config_name):
    check_acl_service_id(service_id)
    config = ServiceConfig.get_one_by_name(service_id, config_name)
    return jsonify(config), 200


@bp.get('/services/<string:service_id>/content')
@cognito_auth_required
@admin_role_editor_required
def get_service_content_list(service_id):
    check_acl_service_id(service_id)
    params = validate_params(schema_get_content(), request.args.to_dict())
    keys = {'serviceId': service_id}
    res = ServiceContent.get_all_pager_new(keys, params)
    return jsonify(res), 200


@bp.get('/services/<string:service_id>/content/<string:content_id>')
@cognito_auth_required
@admin_role_editor_required
def get_service_content_detail(service_id, content_id):
    check_acl_service_id(service_id)
    return get_service_content(service_id, content_id)


@bp.put('/services/<string:service_id>/content/<string:content_id>')
@cognito_auth_required
@admin_role_editor_required
def put_service_content_detail(service_id, content_id):
    check_acl_service_id(service_id)
    service_content = get_service_content(service_id, content_id, False)
    vals = validate_params(schema_put_service_content(), request.json)
    if service_content:
        if service_content.get('commentDefaultPublishStatus') == vals.get('commentDefaultPublishStatus'):
            raise InvalidUsage('Same value', 400)
        keys = {'serviceId': service_id, 'contentId': content_id}
        res = ServiceContent.update_new(keys, vals, True)
        status = 200
    else:
        vals['serviceId'] = service_id
        vals['contentId'] = content_id
        res = ServiceContent.create(vals)
        status = 201
    return jsonify(res), status


@bp.delete('/services/<string:service_id>/content/<string:content_id>')
@cognito_auth_required
@admin_role_editor_required
def delete_service_content(service_id, content_id):
    check_acl_service_id(service_id, True)
    service_content = get_service_content(service_id, content_id, False)
    if not service_content:
        raise InvalidUsage('Target already deleted', 400)

    try:
        keys = {'serviceId': service_id, 'contentId': content_id}
        ServiceContent.delete(keys)
        return jsonify(), 200

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)


mimetype_regex = r'^[0-9a-z_\-\.]+/[0-9a-z_\-\.]+$'


def validation_schema_services():
    return {
        'serviceId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'label': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'empty': False,
        },
        'functions': {
            'type': 'list',
            'required': False,
            'empty': True,
            'default': [],
            'allowed': Service.allowed_functions
        },
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.rtrim),
            'required': False,
            'nullable': True,
            'empty': True,
            'default': '',
        },
        'configs': {
            'type': 'dict',
            'required': False,
            'empty': True,
            'nullable': True,
            'schema': {
                'outerSiteUrl': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'valid_url': True,
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'default': '',
                },
                'frontendPostDetailUrlPrefix': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'valid_url': True,
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'default': '',
                },
                'mediaUploadAcceptMimetypesImage': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'nullable': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': mimetype_regex,
                    }
                },
                'mediaUploadImageSizes': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'nullable': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': r'^[0-9]+x[0-9]+(x[a-z]{1})?$',
                    }
                },
                'mediaUploadSizeLimitMBImage': {
                    'type': 'integer',
                    'coerce': int,
                    'required': False,
                    'empty': True,
                    'nullable': True,
                    'min': 1,
                    'max': 50,
                    'default': 5,
                },
                'mediaUploadAcceptMimetypesFile': {
                    'type': 'list',
                    'coerce': (NormalizerUtils.split),
                    'required': False,
                    'empty': True,
                    'nullable': True,
                    'default': [],
                    'schema': {
                        'type': 'string',
                        'required': False,
                        'empty': True,
                        'regex': mimetype_regex,
                    }
                },
                'mediaUploadSizeLimitMBFile': {
                    'type': 'integer',
                    'coerce': int,
                    'required': False,
                    'empty': True,
                    'nullable': True,
                    'min': 1,
                    'max': 50,
                    'default': 5,
                },
            }
        },
    }


def schema_get_content():
    schema = get_pager_list_schemas | {}
    schema['order']['default'] = 'asc'
    schema['count']['default'] = 50
    return schema


def schema_put_service_content():
    return {
        'commentDefaultPublishStatus': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'nullable': False,
            'allowed': Comment.allowed_vals['publishStatus'],
        },
    }
