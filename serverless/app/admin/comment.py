import os
import traceback
from flask import jsonify, request
from flask_cognito import cognito_auth_required, current_cognito_jwt
from app.models.dynamodb import Comment, CommentCount, ModelInvalidParamsException
from app.common.error import InvalidUsage
from app.common.request import validate_params
from app.validators import NormalizerUtils
from app.validators.schemas.common import get_pager_list_schemas, ulid_schema, content_id_schema
from app.admin import bp, site_before_request, check_acl_service_id, admin_role_editor_required


def get_comment_by_id(comment_id):
    schema = {'commentId': ulid_schema}
    params = {'commentId': comment_id}
    vals = validate_params(schema, params)
    comment = Comment.get_one_by_pkey_new(vals, False, True)
    if not comment:
        raise InvalidUsage('Not Found', 404)
    return comment


@bp.before_request
@site_before_request
def before_request():
    pass


@bp.get('/comments/<string:service_id>')
@cognito_auth_required
@admin_role_editor_required
def get_content_list(service_id):
    check_acl_service_id(service_id, True)

    schema = get_schema_content_list()
    params = validate_params(schema, request.args.to_dict())

    keys = {'serviceId': service_id}
    res = Comment.get_all_pager_new(keys, params, 'commentCreatedAtGsi', True)
    return jsonify(res), 200


@bp.get('/comments/<string:service_id>/content/<string:content_id>')
@cognito_auth_required
@admin_role_editor_required
def get_comment_by_content(service_id, content_id):
    check_acl_service_id(service_id, True)
    schema = get_schema_content_list_by_content()
    add_params = {'contentId': content_id}
    vals = validate_params(schema, request.args.to_dict(), add_params)
    keys = {'serviceIdContentId': f'{service_id}#{content_id}'}
    skey_cond_type = None
    if vals.get('publishStatus'):
        keys['statusCreatedAt'] = vals['publishStatus']
        skey_cond_type = 'begins_with'
    res = Comment.get_all_pager_new(
        keys, vals, 'commentStatusCreatedAtGsi', True, skey_cond_type)
    return jsonify(res), 200


@bp.get('/comments/<string:service_id>/<string:comment_id>')
@cognito_auth_required
@admin_role_editor_required
def get_comment(service_id, comment_id):
    check_acl_service_id(service_id, True)
    comment = get_comment_by_id(comment_id)
    return jsonify(comment), 200


@ bp.delete('/comments/<string:service_id>/<string:comment_id>')
@cognito_auth_required
@admin_role_editor_required
def delete_comment(service_id, comment_id):
    check_acl_service_id(service_id, True)
    comment = get_comment_by_id(comment_id)
    try:
        Comment.delete_and_count_down(comment)
        return jsonify(), 200

    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)

    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)


@ bp.post('/comments/<string:service_id>/<string:comment_id>/status')
@ cognito_auth_required
@ admin_role_editor_required
def post_content_status(service_id, comment_id):
    check_acl_service_id(service_id, True)
    comment = get_comment_by_id(comment_id)
    vals = validate_params(schema_post_comment_status(), request.json)
    new_publish_status = vals['publishStatus']
    if new_publish_status == comment['publishStatus']:
        raise InvalidUsage('Status is same value', 400)

    other_vals = {}
    updated_by = current_cognito_jwt.get('cognito:username', '')
    if updated_by:
        vals['updatedBy'] = updated_by

    try:
        res = Comment.update_publish_status_and_count(
            comment, new_publish_status, other_vals)
    except ModelInvalidParamsException as e:
        raise InvalidUsage(e.message, 400)
    except Exception as e:
        print(traceback.format_exc())
        raise InvalidUsage('Server Error', 500)

    return jsonify(res), 200


def get_schema_content_list():
    return get_pager_list_schemas


def get_schema_content_list_by_content():
    return get_pager_list_schemas | {
        'contentId': content_id_schema,
        'publishStatus': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'nullable': True,
            'allowed': Comment.allowed_vals['publishStatus'],
        },
    }


def schema_post_comment_status():
    return {
        'publishStatus': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'nullable': False,
            'allowed': Comment.allowed_vals['publishStatus'],
        },
    }
