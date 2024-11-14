import re
import json
from cerberus import Validator
from app.common.string import validate_url, validate_email, validate_uuid, validate_base64
from app.common.date import validate_date_str


class ValidatorExtended(Validator):
    def _validate_valid_email(self, email, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (email and value and not validate_email(value)):
            self._error(field, 'email is invalid')

    def _validate_valid_tel(self, tel, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (tel and value and not re.match('^\d{10,11}$', value)):
            self._error(field, 'tel is invalid')

    def _validate_valid_url(self, url, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if (url and value and not validate_url(value)):
            self._error(field, 'url is invalid')

    def _validate_valid_ulid(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_uuid(value, 'ulid'):
                    self._error(field, 'Must be a ulid format')
            else:
                if validate_uuid(value, 'ulid'):
                    self._error(field, 'Must not be a ulid format')

    def _validate_valid_uuid(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_uuid(value, 'uuidv4'):
                    self._error(field, 'Must be a uuidv4 format')
            else:
                if validate_uuid(value, 'uuidv4'):
                    self._error(field, 'Must not be a uuidv4 format')

    def _validate_valid_base64(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_base64(value):
                    self._error(field, 'Must be a base64 format')
            else:
                if validate_base64(value):
                    self._error(field, 'Must not be a base64 format')

    def _validate_valid_date_str(self, constraint, field, value):
        """
        The rule's arguments are validated against this schema: {'type': 'boolean'}
        """
        if value:
            if constraint is True:
                if not validate_date_str(value, '%Y%m%d'):
                    self._error(field, 'Date format is invalid')
            else:
                if validate_date_str(value, '%Y%m%d'):
                    self._error(field, 'Date format is invalid')


class NormalizerExtended(Validator):
    pass


class NormalizerUtils():
    def to_bool(v): return v.lower() in ('true', '1')
    def to_bool_int(v): return 1 if v.lower() in ('true', '1') else 0
    def trim(v): return v.strip() if type(v) is str else v
    def rtrim(v): return v.rstrip() if type(v) is str else v
    split = lambda v, dlt=',': v.split(dlt) if v else []
    def json2dict(v): return json.loads(v) if type(v) is str else None
