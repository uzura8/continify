import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import Tag, Service
from app.common.error import InvalidUsage
from app.common.request import validate_params
from app.validators.schemas.common import get_pager_list_schemas

bp = Blueprint('tag', __name__, url_prefix='/tags')


@bp.route('/<string:service_id>', methods=['GET'])
def handle_list(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = validate_params(schema_get_list(), request.args.to_dict())
    keys = {'serviceId': service_id}
    res = Tag.get_all_pager_new(keys, params, 'TagsByServiceIdGsi')
    return jsonify(res), 200


def schema_get_list():
    schemas = get_pager_list_schemas | {}
    schemas['count']['default'] = 50
    return schemas
