from flask import Blueprint, jsonify, request
from app.models.dynamodb import Post, PostTag, Category, Tag, Service, PostGroup
from app.common.error import InvalidUsage
from app.common.request import validate_req_params, validate_params
from app.common.date import is_future
from app.validators import NormalizerUtils
from app.validators.schemas.common import get_pager_list_schemas, slug_schema

bp = Blueprint('post', __name__, url_prefix='/posts')


@bp.get('/<string:service_id>')
def posts(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    schema = validation_schema_posts_get()
    vals = validate_params(schema, request.args.to_dict())
    vals['status'] = 'publish'

    cate_slug = vals.get('category')
    tag_label = vals.get('tag')
    tag_id = None
    cate = None
    if cate_slug:
        cate = Category.get_one_by_slug(
            service_id, cate_slug, False, True, False, False)
        if not cate:
            raise InvalidUsage('Category does not exist', 404)

    elif tag_label:
        keys = {'serviceId': service_id, 'label': tag_label}
        tag = Tag.get_one_new(keys, 'TagsByServiceIdGsi')
        if not tag:
            raise InvalidUsage('Tag does not exist', 404)
        tag_id = tag['tagId']

    if tag_id:
        # get posts by tag
        keys = {'tagId': tag_id, 'statusPublishAt': 'publish'}
        res = PostTag.get_all_pager_new(
            keys, vals, 'postsByTagGsi', False, 'begins_with')
        if res.get('items'):
            res['meta'] = {'tag': tag}
            keys = [{'postId': pt['postId']} for pt in res['items']]
            posts = Post.batch_get_items(keys)
            post_dict = {post['postId']: post for post in posts}
            for item in res['items']:
                if item['postId'] in post_dict:
                    item.update(post_dict[item['postId']])
    else:
        if cate:
            # get posts by category
            if vals.get('apiVer') == 2:
                # new api version for category
                cate_path = '#'.join([cate['parentPath'], str(cate['id'])])
                status_cate_path = '_'.join(['publish', cate_path])
                keys = {'serviceId': service_id,
                        'statusCategoryPathPublishAt': status_cate_path}
                res = Post.get_all_pager_new(
                    keys, vals, 'statusCategoryPathPublishAtGsi', False, 'begins_with')
            else:
                # old api version for category
                vals['categories'] = [cate_slug]
                if cate['children']:
                    for c in cate['children']:
                        vals['categories'].append(c['slug'])

                pkeys = {'key': 'serviceId', 'val': service_id}
                pager_keys = {'pkey': 'postId', 'index_pkey': 'serviceId',
                              'index_skey': 'statusPublishAt'}
                cate_slugs = vals.get('categories', [])
                filter_conds = {'cate_slugs': cate_slugs}
                res = Post.query_pager_published(
                    pkeys, vals, pager_keys, 'statusPublishAtGsi', filter_conds)

            if vals.get('withCategory', True):
                res['items'] = Post.set_category_to_list(
                    res['items'], service_id)
            res['meta'] = {'category': cate}
        else:
            # get all posts
            keys = {'serviceId': service_id, 'statusPublishAt': 'publish'}
            res = Post.get_all_pager_new(
                keys, vals, 'statusPublishAtGsi', False, 'begins_with')

    return jsonify(res), 200


@bp.route('/<string:service_id>/groups', methods=['GET'])
def post_groups(service_id):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    vals = validate_params(get_pager_list_schemas, request.args.to_dict())
    keys = {'serviceId': service_id}
    res = PostGroup.get_all_pager_new(keys, vals, 'PostGroupsByServiceIdGsi')
    return jsonify(res), 200


@bp.route('/<string:service_id>/groups/<string:slug>', methods=['GET'])
def post_group(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    schema = schema_get_group_post()
    vals = validate_params(schema, request.args.to_dict(), {'slug': slug})

    keys = {'serviceIdSlug': '#'.join([service_id, vals['slug']])}
    group = PostGroup.get_one_by_pkey_new(keys)
    if not group:
        raise InvalidUsage('Not Found', 404)

    posts = []
    post_ids = group.get('postIds', [])
    if post_ids:
        if vals.get('order') == 'desc':
            post_ids.reverse()

        count = vals.get('count')
        if count:
            post_ids = post_ids[:count]

        keys = [{'postId': pid} for pid in post_ids]
        batch_res = Post.batch_get_items(keys)
        for pid in post_ids:
            p = next((p for p in batch_res if p.get('postId') == pid), None)
            posts.append(Post.to_response(p))

    group['posts'] = posts
    group['postIds'] = post_ids

    return jsonify(PostGroup.to_response(group)), 200


@bp.route('/<string:service_id>/<string:slug>', methods=['GET', 'HEAD'])
def post(service_id, slug):
    if not Service.check_exists(service_id):
        raise InvalidUsage('ServiceId does not exist', 404)

    params = {'token': request.args.get('token'), 'slug': slug}
    vals = validate_req_params(validation_schema_post_get(), params)

    item = Post.get_one_by_slug(service_id, slug, True)
    if not item:
        raise InvalidUsage('Not Found', 404)

    is_published = ((item['postStatus'] == 'publish') and (
        item['publishAt'] and not is_future(item['publishAt'])))

    if not is_published:
        if not vals['token'] or vals['token'] != item['previewToken']:
            raise InvalidUsage('Not Found', 404)

    if request.method == 'HEAD':
        return jsonify(), 200

    return jsonify(Post.to_response(item)), 200


validation_schema_slug = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-zA-Z_\-]+$',
}


def validation_schema_post_get():
    return {
        'slug': validation_schema_slug,
        'token': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'required': False,
            'nullable': True,
            'empty': True,
            'regex': r'^[0-9a-fA-F]+$',
        },
    }


def validation_schema_posts_get():
    schemas = get_pager_list_schemas | {
        'category': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'nullable': True,
            'required': False,
            'empty': True,
        },
        'tag': {
            'type': 'string',
            'coerce': (NormalizerUtils.trim),
            'nullable': True,
            'required': False,
            'empty': True,
            'maxlength': 100,
        },
        'withCategory': {
            'type': 'boolean',
            'coerce': (str, NormalizerUtils.to_bool),
            'required': False,
            'empty': True,
            'default': True,
        },
        'apiVer': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 2,
            'default': 1,
        },
        'pagerKey': {
            'type': 'dict',
            'coerce': (NormalizerUtils.json2dict),
            'required': False,
            'nullable': True,
            'empty': True,
            'schema': {
                'serviceId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'postId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'tagId': {
                    'type': 'string',
                    # 'required': True,
                    # 'empty': False,
                },
                'statusPublishAt': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'regex': r'publish#\d{4}\-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}([\+\-]\d{2}:\d{2}|Z)$',
                },
            }
        },
    }
    schemas['order']['default'] = 'desc'
    schemas['count']['default'] = 20
    return schemas


def schema_get_group_post():
    return {
        'slug': slug_schema,
        'count': {
            'type': 'integer',
            'coerce': int,
            'required': False,
            'min': 1,
            'max': 50,
            'default': 5,
        },
        'order': {
            'type': 'string',
            'required': False,
            'allowed': ['asc', 'desc'],
            'default': 'asc',
        },
    }
