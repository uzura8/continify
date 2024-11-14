from urllib.parse import quote, urlparse
from app.models.dynamodb.base import Base, ModelInvalidParamsException
from app.models.dynamodb.service_config import ServiceConfig
from app.models.dynamodb.shorten_url_domain import ShortenUrlDomain
from app.common.string import random_str
from app.common.date import utc_iso
from app.common.url import join_query


class ShortenUrl(Base):
    table_name = 'shorten-url'
    public_attrs = [
        'urlId',
        'serviceSeqNumber',
        'locationTo',
        'createdAt',
        'updatedAt',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'serviceId',
        'url',
        'isViaJumpPage',
        'paramKey',
        'paramValue',
        'confirmStatus',
        'assigneeName',
        'assigneeMemo',
        'createdBy',
        'confirmedAt',
        'name',
        'description',
        'domain'
        'serviceIdDomain',
        'confirmStatusCreatedAt',
        'urlCreatedAt',
    ]
    all_attrs = public_attrs + private_attrs

    allowed_vals = {
        'confirmStatus': ['unconfirmed', 'confirmed'],
    }

    @classmethod
    def query_pager(self, hkey=None, params=None):
        index = params.get('index')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 20)
        start_key = params.get('ExclusiveStartKey')

        table = self.get_table()

        key_cond_exps = []
        exp_attr_names = {}
        exp_attr_vals = {}
        option = {
            'ScanIndexForward': not is_desc,
            'Limit': limit,
        }
        if index:
            option['IndexName'] = index

        if hkey is not None:
            key_cond_exps.append('#hk = :hv')
            exp_attr_names['#hk'] = hkey['name']
            exp_attr_vals[':hv'] = hkey['value']

        if key_cond_exps:
            option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
            option['ExpressionAttributeNames'] = exp_attr_names
            option['ExpressionAttributeValues'] = exp_attr_vals

        if start_key:
            option['ExclusiveStartKey'] = start_key

        res = table.query(**option)
        items = res['Items']

        return {
            'items': items,
            'pagerKey': res['LastEvaluatedKey'] if 'LastEvaluatedKey' in res else None,
        }

    @classmethod
    def get_new_url_id(self):
        url_id = ''
        url = ''
        i = 0
        limit = 10
        while not url_id or (url and i < limit):
            url_id = random_str(10)
            keys = {'urlId': url_id}
            url = self.get_one_by_pkey_new(keys)
            i += 1
        return url_id

    @classmethod
    def create_item(self, params, params_val_prefix=None):
        vals = {} | params

        service_id = vals.get('serviceId')
        if not service_id:
            raise Exception('ServiceId is required')

        if vals.get('urlId'):
            url_id = vals['urlId']
            item = self.get_one_by_pkey_new({'urlId': url_id})
            if item:
                raise Exception('UrlId already exists')
        else:
            url_id = self.get_new_url_id()
            if not url_id:
                raise Exception('Create new url_id failed')
        vals['urlId'] = url_id

        parsed_url = urlparse(vals.get('url'))
        domain = parsed_url.netloc
        vals['domain'] = domain
        vals['serviceIdDomain'] = f'{service_id}#{domain}'

        created_at = vals.get('createdAt')
        if not created_at:
            created_at = utc_iso(False, True)
        vals['createdAt'] = created_at
        vals['urlCreatedAt'] = '|'.join([vals['url'], created_at])

        if vals.get('confirmStatus') is not None:
            confirm_status = vals['confirmStatus']
            if confirm_status not in self.allowed_vals['confirmStatus']:
                raise Exception('Invalid confirmStatus value')
        else:
            is_confirmed = bool(vals.get('isConfirmed', False))
            if 'isConfirmed' in vals:
                del vals['isConfirmed']
            confirm_status = 'confirmed' if is_confirmed else 'unconfirmed'
        vals['confirmStatus'] = confirm_status
        vals['confirmStatusCreatedAt'] = '#'.join([confirm_status, created_at])
        if confirm_status == 'confirmed':
            vals['confirmedAt'] = created_at

        seq_num = ServiceConfig.increment_number(
            service_id, 'shortenUrlSeqNumber')
        zero_pad_num = str(seq_num).zfill(5)
        vals['locationTo'] = self.generate_redirect_url(
            service_id, vals, params_val_prefix, zero_pad_num)
        vals['serviceSeqNumber'] = seq_num

        res = ShortenUrl.create(vals)
        ShortenUrlDomain.check_not_exists_and_create_item(
            service_id, domain)
        return res

    @classmethod
    def update_item(self, url_id, params, params_val_prefix=None):
        vals = {} | params

        service_id = vals.get('serviceId')
        if not service_id:
            raise Exception('ServiceId is required')

        keys = {'urlId': url_id}
        saved = self.get_one_by_pkey_new(keys, True, True)
        if not saved:
            raise Exception('Update item not exists')

        seq_num = str(saved['serviceSeqNumber']).zfill(
            5) if saved.get('serviceSeqNumber') else None
        vals['locationTo'] = self.generate_redirect_url(
            service_id, vals, params_val_prefix, seq_num)

        domain_upd = ''
        created_at = saved['createdAt']
        if vals.get('url') and vals['url'] != saved['url']:
            parsed_url = urlparse(vals.get('url'))
            domain_upd = parsed_url.netloc
            vals['serviceIdDomain'] = f'{service_id}#{domain_upd}'
            vals['domain'] = domain_upd
            vals['urlCreatedAt'] = '|'.join([vals['url'], created_at])

        is_confirmed = bool(vals.get('isConfirmed', False))
        if 'isConfirmed' in vals:
            del vals['isConfirmed']
        confirm_status = 'confirmed' if is_confirmed else 'unconfirmed'
        if confirm_status != saved.get('confirmStatus'):
            vals['confirmStatus'] = confirm_status
            vals['confirmStatusCreatedAt'] = '#'.join(
                [confirm_status, created_at])
            if confirm_status == 'confirmed':
                vals['confirmedAt'] = utc_iso(False, True)

        updated = ShortenUrl.update_new(keys, vals, True)
        if domain_upd and domain_upd != saved['domain']:
            ShortenUrlDomain.check_exists_and_delete_item(
                service_id, saved['domain'])
            # If new domain not saved, Add new domain to domains table
            ShortenUrlDomain.check_not_exists_and_create_item(
                service_id, domain_upd)
        return updated

    @staticmethod
    def generate_redirect_url(service_id, vals, prefix=None, suffix=None):
        service_confs = ServiceConfig.get_all_by_service(
            service_id, True, True, True)
        url = vals.get('url')
        pkey = vals.get('paramKey')
        pval = vals.get('paramValue')
        via_jump = vals.get('isViaJumpPage')

        if pval:
            items = [pval]
            if prefix:
                items.insert(0, prefix)
            if suffix:
                items.append(suffix)
            pval = '-'.join(items)

        add_query = ''
        if pkey and pval:
            add_query = '%s=%s' % (pkey, pval)

        if via_jump:
            has_jump_data = (service_confs
                             and service_confs.get('jumpPageUrl')
                             and service_confs.get('jumpPageParamKey'))
            if not has_jump_data:
                raise ModelInvalidParamsException('JumpPage data not exists')

            jump_page = service_confs['jumpPageUrl']
            jump_pkey = service_confs['jumpPageParamKey']

            quoted = quote(url, safe='')
            if add_query:
                add_query += '&'
            add_query += '%s=%s' % (jump_pkey, quoted)
            res = join_query(jump_page, add_query)

        else:
            res = join_query(url, add_query)

        return res
