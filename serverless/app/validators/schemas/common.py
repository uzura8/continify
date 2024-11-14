from app.validators import NormalizerUtils

ulid_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'valid_ulid': True,
}

# For Firebase Auth UID
user_id_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'regex': r'^[a-zA-Z0-9\-_]{28,32}$',
}

slug_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-z\-]+$',
}

random_slug_schema = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': True,
    'empty': False,
    'maxlength': 128,
    'regex': r'^[0-9a-zA-Z_\-]+$',
}

content_id_schema = {
    'type': 'string',
    'coerce': (NormalizerUtils.trim),
    'required': True,
    'nullable': False,
    'empty': False,
    'regex': r'^[0-9a-z_\-]{4,64}$',
}

get_list_schemas = {
    'count': {
        'type': 'integer',
        'coerce': int,
        'required': False,
        'min': 1,
        'max': 50,
        'default': 10,
    },
    'order': {
        'type': 'string',
        'required': False,
        'allowed': ['asc', 'desc'],
        'default': 'asc',
    },
}

schema_page_token = {
    'type': 'string',
    'coerce': (str, NormalizerUtils.trim),
    'required': False,
    'empty': True,
    'valid_base64': True,
}

get_pager_list_schemas = {
    'pageToken': schema_page_token,
    'count': {
        'type': 'integer',
        'coerce': int,
        'required': False,
        'min': 1,
        'max': 50,
        'default': 10,
    },
    'order': {
        'type': 'string',
        'required': False,
        'allowed': ['asc', 'desc'],
        'default': 'asc',
    },
}

schema_with_detail = {
    'type': 'boolean',
    'coerce': (str, NormalizerUtils.to_bool),
    'required': False,
    'empty': True,
    'default': False,
}
