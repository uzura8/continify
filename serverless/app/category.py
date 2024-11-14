import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Category, Service
from app.common.error import InvalidUsage
from app.common.request import validate_req_params, validate_params
from app.validators import NormalizerUtils
from app.validators.schemas.common import ulid_schema, user_id_schema, slug_schema, random_slug_schema, get_list_schemas, schema_page_token

bp = Blueprint('category', __name__, url_prefix='/categories')


@bp.route('/<string:service_id>', methods=['GET'])
def handle_list(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    vals = validate_req_params(validation_schema_list_get(), request.args)
    is_nested = not vals.get('isList')
    body = Category.get_all_by_service_id(service_id, True, is_nested)
    return jsonify(body), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['GET', 'HEAD'])
def handle_detail(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    vals = validate_params(
        schema_get_detail(), request.args.to_dict(), {'slug': slug})

    # API version 1 params
    with_parents = vals.get('withParents', False)
    with_children = vals.get('withChildren', False)
    # API version 2 params
    with_parent = vals.get('withParent', False)
    sub_scope = vals.get('subScope', None)

    if request.method == 'HEAD':
        with_parents = False
        with_children = False
        with_parent = False
        sub_scope = None

    if vals.get('apiVer', 1) == 2:
        item = Category.get_one_by_slug_new(
            service_id, vals['slug'], with_parent, sub_scope)
    else:
        item = Category.get_one_by_slug(
            service_id, vals['slug'], with_parents, with_children, True)

    if not item:
        item = []
        # raise InvalidUsage('Not Found', 404)

    if request.method == 'HEAD':
        if not item:
            raise InvalidUsage('Not Found', 404)
        return jsonify(), 200

    return jsonify(item), 200


@bp.route('/<string:service_id>/<string:slug>/children', methods=['GET'])
def handle_detail_childlen(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    parent = Category.get_one_by_slug(
        service_id, slug, False, False, True, False)
    if not parent:
        raise InvalidUsage('Not Found', 404)

    if parent['parentPath'] == '0':
        parent_path = str(parent['id'])
    else:
        parent_path = '#'.join([parent['parentPath'], str(parent['id'])])

    items = Category.get_children_by_parent_path(
        service_id, parent_path, False, True, False)
    if not items:
        items = []

    return jsonify(items), 200


def validation_schema_detail_get():
    return {
        'slug': slug_schema,
        'withParent': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'subScope': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'allowed': ['all', 'direct', 'skipChildren'],
        },
    }


def validation_schema_list_get():
    return {
        'isList': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
    }


def schema_get_detail():
    return {
        'slug': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'maxlength': 128,
            'regex': r'^[0-9a-z\-]+$',
        },
        'withParents': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'withChildren': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'withParent': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': False,
        },
        'subScope': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': False,
            'empty': True,
            'allowed': ['all', 'direct', 'skipChildren'],
        },
        'apiVer': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 2,
            'default': 1,
        },
    }
