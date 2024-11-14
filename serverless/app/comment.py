import os
from flask import Blueprint, jsonify, request, current_app
from app.models.dynamodb import (
    Comment,
    CommentCount,
    Service,
    ServiceConfig,
    ServiceContent,
    ModelInvalidParamsException,
)
from app.common.error import InvalidUsage
from app.common.request import validate_params
from app.common.date import utc_iso
from app.validators import NormalizerUtils
from app.validators.schemas.common import slug_schema, get_pager_list_schemas, content_id_schema
from app.common.recaptcha import verify_recaptcha


bp = Blueprint('comment', __name__, url_prefix='/comments')

COMMENT_DEFAULT_PUBLISH_STATUS = os.environ.get(
    'COMMENT_DEFAULT_PUBLISH_STATUS', False)


@bp.route('/<string:service_id>/counts', methods=['GET'])
def comment_counts(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    pkeys = {'key': 'serviceId', 'val': service_id}
    items = CommentCount.get_all_by_pkey(pkeys, None, None, False)
    body = conv_res_obj_for_all_count(items)
    return jsonify(body), 200


@bp.get('/<string:service_id>/<string:content_id>')
def get_comments(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    schema = schema_get_comments()
    add_params = {'serviceId': service_id, 'contentId': content_id}
    vals = validate_params(schema, request.args.to_dict(), add_params)
    keys = {
        'serviceIdContentId': '#'.join([service_id, content_id]),
        'statusCreatedAt': 'publish',
    }
    res_body = Comment.get_all_pager_new(
        keys, vals, 'commentStatusCreatedAtGsi', False, 'begins_with')

    count_keys = {
        'serviceId': service_id,
        'contentIdPublishStatus': '#'.join([content_id, 'publish']),
    }
    count = 0
    count_item = CommentCount.get_one_by_pkey_new(count_keys)
    if count_item:
        count = count_item.get('commentCount', 0)
    res_body['meta'] = {'count': count}

    return jsonify(res_body), 200


@bp.post('/<string:service_id>/<string:content_id>')
def post_comment(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    req_vals = request.json
    schema = schema_post_comment()
    add_vals = {'serviceId': service_id, 'contentId': content_id}
    vals = validate_params(schema, req_vals, add_vals)

    if current_app.config['RECAPTCHA_ENABLED']:
        if not vals.get('recaptcha'):
            raise InvalidUsage('Recaptcha is required',
                               400, {'recaptcha': 'Recaptcha is required'})
        secret_key = current_app.config['RECAPTCHA_SECRET_KEY']
        success, score, action = verify_recaptcha(
            vals['recaptcha'], secret_key)
        if action != 'comment':
            raise InvalidUsage('Recaptcha action is invalid', 400)
        if not success or score < 0.5:
            raise InvalidUsage('Recaptcha verification failed', 400)

    # Check if the content setting is set
    publish_status = COMMENT_DEFAULT_PUBLISH_STATUS
    keys = {'serviceId': service_id}
    params = {'count': 100}
    service_content_list = ServiceContent.get_all_new(keys, params)
    if service_content_list:
        target_content = next(
            (x for x in service_content_list if x.get('contentId') == content_id), None)
        if not target_content:
            raise InvalidUsage('ContentId does not accepted', 400)
        publish_status = target_content.get('commentDefaultPublishStatus')
    else:
        if config := ServiceConfig.get_val(service_id, 'commentDefaultPublishStatus'):
            publish_status = config
    vals['publishStatus'] = publish_status

    try:
        res_body = Comment.create_and_count_up(vals, True)

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    return jsonify(res_body), 200


def conv_res_obj_for_all_count(items):
    res_body = {
        'items': [],
        'totalCount': 0,
    }

    if items:
        res_body['items'] = items
        count = 0
        for item in items:
            count += item.get('commentCount', 0)
        res_body['totalCount'] = count

    return res_body


def schema_get_comments():
    return {
        'serviceId': slug_schema,
        'contentId': content_id_schema,
        'pagerKey': {
            'type': 'dict',
            'coerce': (NormalizerUtils.json2dict),
            'required': False,
            'nullable': True,
            'empty': True,
            'schema': {
                'commentId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'serviceIdContentId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'statusCreatedAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'publish#\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    } | get_pager_list_schemas


def schema_post_comment():
    return {
        'serviceId': slug_schema,
        'contentId': content_id_schema,
        'body': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': True,
            'nullable': False,
            'empty': False,
            'maxlength': 1000,
        },
        'recaptcha': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
        },
        'profiles': {
            'type': 'dict',
            # 'coerce': (NormalizerUtils.json2dict),
            'required': True,
            'nullable': True,
            'empty': True,
            'default': {},
            'schema': {
                'nickname': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'maxlength': 50,
                },
                'age': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'maxlength': 20,
                },
                'area': {
                    'type': 'string',
                    'coerce': (NormalizerUtils.trim),
                    'required': False,
                    'nullable': True,
                    'empty': True,
                    'maxlength': 50,
                },
            }
        },
    }


def validation_schema_comments():
    return {
        'contentId': content_id_schema,
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 100,
            'default': 10,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'desc',
        },
        'pagerKey': {
            'type': 'dict',
            'coerce': (NormalizerUtils.json2dict),
            'required': False,
            'nullable': True,
            'empty': True,
            'schema': {
                'commentId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'serviceIdContentId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'statusCreatedAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'publish#\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    }
