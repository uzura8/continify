import os
from flask import Blueprint, jsonify, request
from app.models.dynamodb import VoteCount, VoteLog, Service
from app.common.error import InvalidUsage
from app.validators import NormalizerUtils
from app.common.request import validate_req_params

bp = Blueprint('vote', __name__, url_prefix='/votes')


@bp.get('/<string:service_id>')
def get_vote_by_service(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {}
    for key in ['contentIds']:
        params[key] = request.args.get(key)
    vals = validate_req_params(validation_schema_vote(), params)

    if vals.get('contentIds'):
        body = VoteCount.query_all_by_contentIds(
            service_id, vals['contentIds'])
    else:
        keys = {'p': {'key': 'serviceId', 'val': service_id}}
        items = VoteCount.get_all(keys)
        body = conv_res_obj_for_all_votes(items)
    return jsonify(body), 200


@bp.get('/<string:service_id>/<string:content_id>')
def get_votes_by_content(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'contentId': content_id}
    vals = validate_req_params(validation_schema_vote(), params)
    items = get_votes_by_content_id(service_id, vals['contentId'])
    body = conv_res_obj_for_all_votes(items)
    return jsonify(body), 200


@bp.post('/<string:service_id>/<string:content_id>')
def post_vote_by_content(service_id, content_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'contentId': content_id}
    vals = validate_req_params(validation_schema_vote(), params)
    vote_type = request.json.get('type', 'like').strip()
    if not vote_type:
        raise InvalidUsage('Type is invalid', 400)

    meta_info = request.json.get('metaInfo')
    item = {
        'serviceId': service_id,
        'contentId': vals['contentId'],
        'voteType': vote_type,
        'ip': request.remote_addr,
        'ua': request.headers.get('User-Agent', ''),
    }
    VoteLog.create(item)
    VoteCount.update_count(
        service_id, vals['contentId'], vote_type, meta_info)

    items = get_votes_by_content_id(service_id, vals['contentId'])
    return jsonify(items), 200


def get_votes_by_content_id(service_id, content_id):
    keys = {
        'p': {'key': 'serviceId', 'val': service_id},
        's': {'key': 'contentId', 'val': content_id},
    }
    proj_exps = 'serviceId, contentId, voteType, voteCount, updatedAt, metaInfo'
    items = VoteCount.get_all(
        keys, False, 'ServiceIdContentIdLsi', 0, proj_exps)
    return items


def conv_res_obj_for_all_votes(items):
    res_body = {
        'items': [],
        'totalCount': 0,
    }

    if items:
        res_body['items'] = items
        count = 0
        for item in items:
            count += item['voteCount']
        res_body['totalCount'] = count

    return res_body


def validation_schema_vote():
    return {
        'contentId': {
            'type': 'string',
            'coerce': (str, NormalizerUtils.trim),
            'required': True,
            'empty': False,
            'minlength': 4,
            'maxlength': 36,
            'regex': r'^[0-9a-z_\-]+$',
        },
        'contentIds': {
            'type': 'list',
            'coerce': (NormalizerUtils.split),
            'required': False,
            'empty': True,
            'default': [],
            'schema': {
                'type': 'string',
                'required': False,
                'empty': True,
                'minlength': 4,
                'maxlength': 36,
                'regex': r'^[0-9a-z_\-]+$',
            }
        },
    }
