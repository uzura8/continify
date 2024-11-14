import base64
import boto3
import json
import os
from app.common.date import utc_iso
from app.common.string import new_uuid
from app.common.decimal_encoder import decimal_default


class Base():
    __abstract__ = True

    IS_LOCAL = os.getenv('IS_LOCAL', 'False').lower() == 'true'
    PRJ_PREFIX = os.environ['PRJ_PREFIX']

    reserved_values = None

    @classmethod
    def connect_dynamodb(self):
        if self.IS_LOCAL:
            dynamodb = boto3.resource(
                'dynamodb', endpoint_url='http://localhost:8000')
        else:
            dynamodb = boto3.resource('dynamodb')
        return dynamodb

    @classmethod
    def get_table(self, table_name=None):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        return dynamodb.Table(table_name)

    @classmethod
    def get_table_name(self):
        return '-'.join([self.PRJ_PREFIX, self.table_name])

    @classmethod
    def prj_exps_str(self, is_public=True):
        attrs = self.public_attrs if is_public else self.all_attrs
        res = [attr['key'] if isinstance(
            attr, dict) else attr for attr in attrs]
        return ', '.join(res)

    @classmethod
    def to_response(self, item):
        res = {}
        for i in self.response_attrs:
            if isinstance(i, str):
                k = i
                l = i
            if isinstance(i, dict):
                k = i['key']
                l = i['label']

            if k in item:
                val = item.get(k)
                if val:
                    res[l] = val

        return res

    @classmethod
    def scan(self, options=None, is_return_raw=False):
        if options is None:
            options = {}
        table = self.get_table()
        res = table.scan(**options)

        if is_return_raw:
            return res

        return res.get('Items', [])

    @classmethod
    def scan_all(self):
        table = self.get_table()
        items = []
        params = {}
        while True:
            res = table.scan(**params)
            items.extend(res['Items'])
            if ('LastEvaluatedKey' in res):
                params['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break
        return items

    @classmethod
    def get_all(self, keys, is_desc=False, index_name=None, limit=0, projections=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        if projections:
            if isinstance(projections, list):
                projections = ', '.join(projections)
            option['ProjectionExpression'] = projections

        if index_name:
            option['IndexName'] = index_name

        if not keys.get('p'):
            raise ModelInvalidParamsException("'p' is required on keys")

        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': keys['p']['key']}
        exp_attr_vals = {':pk': keys['p']['val']}

        if keys.get('s'):
            exp_attr_names['#sk'] = keys['s']['key']
            exp_attr_vals[':sk'] = keys['s']['val']
            key_cond_exps.append('#sk = :sk')

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'] if len(res['Items']) > 0 else []

    @classmethod
    def get_one(self, keys, is_desc=False, index_name=None, projections=None):
        items = self.get_all(keys, is_desc, index_name, 1, projections)
        return items[0] if len(items) > 0 else None

    @classmethod
    def get_all_by_pkey(self, pkeys, params=None, index_name=None, is_all_attr=True):
        table = self.get_table()

        if params and params.get('order') and not params.get('is_desc'):
            if params is None:
                params = {}
            params['is_desc'] = params.get('order') == 'desc'

        option = {'ScanIndexForward': not (
            params and params.get('is_desc', False))}

        if params and params.get('count'):
            option['Limit'] = params['count']

        if index_name:
            option['IndexName'] = index_name

        key_cond_exp = '#pk = :pk'
        exp_attr_names = {'#pk': pkeys['key']}
        exp_attr_vals = {':pk': pkeys['val']}

        option['KeyConditionExpression'] = key_cond_exp
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        items = res.get('Items')
        if is_all_attr:
            return items

        return [self.to_response(item) for item in items]

    @classmethod
    def get_one_by_pkey(self, hkey_name, hkey_val, is_desc=False, index_name=None):
        table = self.get_table()
        option = {
            'ScanIndexForward': not is_desc,
            'Limit': 1,
        }
        if index_name:
            option['IndexName'] = index_name
        exp_attr_names = {}
        exp_attr_vals = {}
        exp_attr_names['#hk'] = hkey_name
        exp_attr_vals[':hv'] = hkey_val
        option['KeyConditionExpression'] = '#hk = :hv'
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        return res['Items'][0] if len(res['Items']) > 0 else None

    @classmethod
    def get_one_by_pkey_new(self, keys, consistent_read=False, is_all_attrs=False):
        table = self.get_table()
        get_item_kwargs = {
            'Key': keys
        }
        if consistent_read:
            get_item_kwargs['ConsistentRead'] = True

        res = table.get_item(**get_item_kwargs)
        item = res.get('Item')
        if not item:
            return None
        return item if is_all_attrs else self.to_response(item)

    @classmethod
    def get_one_new(self, keys, index=None, is_all_attrs=False, is_desc=False):
        """
        keys = {
            'pkey': 'pkey_value',
            'skey': 'skey_value',
        }
        """
        params = {'count': 1}
        if is_desc:
            params['order'] = 'desc'
        items = self.get_all_new(keys, params, index, is_all_attrs)
        return items[0] if len(items) > 0 else None

    @classmethod
    def get_all_new(self, keys, params=None, index=None, is_all_attrs=False, skey_cond_type='eq'):
        res = self.get_all_pager_new(
            keys, params, index, is_all_attrs, skey_cond_type)
        return res['items']

    @classmethod
    def get_all_pager_new(self, keys, params=None, index=None, is_all_attrs=False, skey_cond_type='eq'):
        """
        keys = {
            'pkey': 'pkey_value',
            'skey': 'skey_value',
        }
        params = {
            'order': 'asc' or 'desc',
            'count': number,
            'pagerKey': {},
        }
        """
        table = self.get_table()

        if params is None:
            params = {}

        is_desc = False
        limit = 50
        if params:
            is_desc = params.get('order', 'asc') == 'desc'
            limit = params.get('count', 50)
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        pager_key = None
        if params.get('pagerKey'):
            pager_key = params['pagerKey']
        elif params.get('pageToken'):
            pager_key = json.loads(base64.b64decode(
                params['pageToken']).decode('utf-8'))
        if pager_key:
            option['ExclusiveStartKey'] = pager_key

        # if projections:
        #     if isinstance(projections, list):
        #         projections = ', '.join(projections)
        #     option['ProjectionExpression'] = projections

        if index:
            option['IndexName'] = index

        if not isinstance(keys, dict) or len(keys) == 0:
            raise ModelInvalidParamsException("'pkey' is required on keys")

        key_items = list(keys.items())
        pkey, pval = key_items[0]
        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': pkey}
        exp_attr_vals = {':pk': pval}

        if len(key_items) > 1:
            skey, sval = key_items[1]
            exp_attr_names['#sk'] = skey
            exp_attr_vals[':sk'] = sval
            if skey_cond_type == 'begins_with':
                key_cond_exps.append('begins_with(#sk, :sk)')
            else:
                if skey_cond_type == 'ne':
                    skey_ope = '<>'
                elif skey_cond_type == 'ge':
                    skey_ope = '>='
                elif skey_cond_type == 'gt':
                    skey_ope = '>'
                elif skey_cond_type == 'lt':
                    skey_ope = '<'
                elif skey_cond_type == 'le':
                    skey_ope = '<='
                elif skey_cond_type == 'eq':
                    skey_ope = '='
                else:
                    skey_ope = '='
                key_cond_exps.append(f'#sk {skey_ope} :sk')

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        items = res.get('Items', [])

        next_pager_key = res.get('LastEvaluatedKey')
        next_page_token = None
        if next_pager_key:
            next_page_token = base64.b64encode(json.dumps(
                next_pager_key, default=decimal_default).encode('utf-8')).decode('utf-8')

        if not is_all_attrs:
            return {
                'items': [self.to_response(item) for item in items],
                'pagerKey': next_pager_key,
                'pageToken': next_page_token
            }
        return {
            'items': items,
            'pagerKey': next_pager_key,
            'pageToken': next_page_token
        }

    @classmethod
    def delete(self, key_dict):
        table = self.get_table()
        res = table.delete_item(
            Key=key_dict
        )
        return res

    @classmethod
    def delete_table(self):
        table = self.get_table()
        res = table.delete()
        return res

    @classmethod
    def get_reserved_values(self, attr):
        if not self.reserved_values:
            return []

        if attr not in self.reserved_values:
            return []

        return self.reserved_values[attr]

    @classmethod
    def check_set_reserved_value(self, vals, is_raise_exp=True):
        if not self.reserved_values:
            return False

        for attr in self.reserved_values:
            if attr not in vals:
                continue

            if vals[attr] in self.reserved_values[attr]:
                if is_raise_exp:
                    raise ModelInvalidParamsException(
                        '%s value is not allowed' % attr)
                else:
                    return True

        return False

    @classmethod
    def create(self, vals, uuid_name=None):
        if not vals.get('createdAt'):
            if vals.get('updatedAt'):
                vals['createdAt'] = vals['updatedAt']
            else:
                vals['createdAt'] = utc_iso(False, True)

        self.check_set_reserved_value(vals)

        if uuid_name:
            vals[uuid_name] = new_uuid()

        table = self.get_table()
        table.put_item(Item=vals)
        return vals

    @classmethod
    def update(self, query_keys, vals, is_update_time=False):
        self.check_set_reserved_value(vals)

        table = self.get_table()

        if is_update_time:
            vals['updatedAt'] = utc_iso(False, True)

        update_attrs = {}
        for key, val in vals.items():
            update_attrs[key] = {'Value': val}

        update_keys = {}
        for key_type, key_dict in query_keys.items():
            key_name = key_dict['key']
            update_keys[key_name] = key_dict['val']
        res = table.update_item(
            Key=update_keys,
            AttributeUpdates=update_attrs,
        )
        items = self.get_one(query_keys)
        return items

    @classmethod
    def update_pk_value(self, current_keys, update_vals, is_update_time=False):
        item = self.get_one(current_keys)
        for attr, val in update_vals.items():
            item[attr] = val

        if is_update_time:
            item['updatedAt'] = utc_iso(False, True)

        key_dict = {}
        pkey = current_keys['p']['key']
        key_dict[pkey] = current_keys['p']['val']
        if 's' in current_keys:
            skey = current_keys['s']['key']
            key_dict[skey] = current_keys['s']['val']

        self.delete(key_dict)
        return self.create(item)

    @classmethod
    def update_new(self, keys, vals, is_update_time=False):
        """
        keys = {
            'pkey': 'pkey_value',
            'skey': 'skey_value',
        }
        """
        self.check_set_reserved_value(vals)
        table = self.get_table()

        if is_update_time:
            vals['updatedAt'] = utc_iso()

        update_attrs = {}
        for key, val in vals.items():
            update_attrs[key] = {'Value': val}

        res = table.update_item(
            Key=keys,
            AttributeUpdates=update_attrs,
        )
        items = self.get_one_by_pkey_new(keys, True, True)
        return items

    @classmethod
    def batch_get_items(self, keys):
        dynamodb = self.connect_dynamodb()
        table_name = self.get_table_name()
        res = dynamodb.batch_get_item(
            RequestItems={
                table_name: {
                    'Keys': keys,
                    'ConsistentRead': True
                }
            },
            ReturnConsumedCapacity='TOTAL'
        )
        return res['Responses'][table_name]

    @classmethod
    def batch_save(self, items, pkeys=None, is_overwrite=False):
        table = self.get_table()
        overwrite_by_pkeys = pkeys if is_overwrite and pkeys else []
        with table.batch_writer(overwrite_by_pkeys=overwrite_by_pkeys) as batch:
            for item in items:
                # target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.put_item(target_keys)

    @classmethod
    def batch_delete(self, items, pkeys=None):
        table = self.get_table()
        with table.batch_writer() as batch:
            for item in items:
                # target_keys = {k: v for k, v in item.items() if k in pkeys or not pkeys}
                target_keys = {k: v for k, v in item.items()}
                batch.delete_item(target_keys)

    @classmethod
    def truncate(self):
        table = self.get_table()
        delete_items = []
        params = {}
        while True:
            res = table.scan(**params)
            delete_items.extend(res['Items'])
            if ('LastEvaluatedKey' in res):
                params['ExclusiveStartKey'] = res['LastEvaluatedKey']
            else:
                break

        key_names = [x['AttributeName'] for x in table.key_schema]
        delete_keys = [{k: v for k, v in x.items() if k in key_names}
                       for x in delete_items]

        with table.batch_writer() as batch:
            for key in delete_keys:
                batch.delete_item(Key=key)

    @classmethod
    def update_add_values(self, keys, add_vals, is_return_updated_item=False):
        if all(x == 0 for x in add_vals.values()):
            return

        table = self.get_table()
        upd_exp = []
        upd_vals = {}
        for k, v in add_vals.items():
            upd_exp.append(f'{k} :{k}')
            upd_vals[f':{k}'] = v

        upd_exp_str = 'ADD ' + ', '.join(upd_exp)
        res = table.update_item(
            Key=keys,
            UpdateExpression=upd_exp_str,
            ExpressionAttributeValues=upd_vals
        )

        if is_return_updated_item:
            return self.get_one_by_pkey_new(keys, True, True)
        else:
            return res

    @staticmethod
    def get_count_up_and_update_options(keys, add_vals, update_vals=None):
        upd_exp_add = []
        upd_vals = {}
        for k, v in add_vals.items():
            upd_exp_add.append(f'{k} :{k}')
            upd_vals[f':{k}'] = v

        upd_exp_set = []
        if update_vals:
            for k, v in update_vals.items():
                upd_exp_set.append(f'{k} = :{k}')
                upd_vals[f':{k}'] = v

        upd_exp_str = ''
        if upd_exp_add:
            upd_exp_str += 'ADD ' + ', '.join(upd_exp_add)
        if upd_exp_set:
            if upd_exp_str:
                upd_exp_str += ' '
            upd_exp_str += 'SET ' + ', '.join(upd_exp_set)

        return {
            'Key': keys,
            'UpdateExpression': upd_exp_str,
            'ExpressionAttributeValues': upd_vals
        }

    @classmethod
    def count_up_and_update_values(self, keys, add_vals, update_vals=None, is_return_updated_item=False):
        if all(x == 0 for x in add_vals.values()):
            return

        table = self.get_table()
        options = self.get_count_up_and_update_options(
            keys, add_vals, update_vals)
        res = table.update_item(**options)

        if is_return_updated_item:
            return self.get_one_by_pkey(keys, True, True)
        else:
            return res

    @classmethod
    def query_pager_published(self, pkeys, params, pager_keys_def, index_name=None, filter_conds=None):
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 20)

        option = {
            'IndexName': index_name,
            'ProjectionExpression': self.prj_exps_str(),
            'ScanIndexForward': not is_desc,
        }
        if index_name:
            option['IndexName'] = index_name

        key_conds = []
        exp_attr_names = {}
        exp_attr_vals = {}

        key_conds.append('#pk = :pk')
        exp_attr_names['#pk'] = pkeys['key']
        exp_attr_vals[':pk'] = pkeys['val']

        # start_key = params.get('pagerKey')
        pager_key = None
        if params.get('pagerKey'):
            pager_key = params['pagerKey']
        elif params.get('pageToken'):
            pager_key = json.loads(base64.b64decode(
                params['pageToken']).decode('utf-8'))
        # if pager_key:
        #     option['ExclusiveStartKey'] = pager_key

        status = 'publish'
        key_conds.append('begins_with(#sk, :sk)')
        exp_attr_names['#sk'] = pager_keys_def['index_skey']
        exp_attr_vals[':sk'] = status

        filter_exps_str = ''
        if filter_conds:
            exp_attr_names, exp_attr_vals, filter_exps_str =\
                self.get_filter_exps_for_pager_published(
                    exp_attr_names, exp_attr_vals, filter_conds)

        if filter_exps_str:
            option['FilterExpression'] = filter_exps_str

        option['KeyConditionExpression'] = ' AND '.join(key_conds)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals

        items, next_pager_key = self.query_loop_for_limit(option, limit, pager_key,
                                                          pager_keys_def, len(filter_exps_str) > 0)
        next_page_token = None
        if next_pager_key:
            next_page_token = base64.b64encode(json.dumps(
                next_pager_key, default=decimal_default).encode('utf-8')).decode('utf-8')

        return {
            'items': items,
            'pagerKey': next_pager_key,
            'pageToken': next_page_token,
        }

    @classmethod
    def get_filter_exps_for_pager_published(self, exp_attr_names, exp_attr_vals, filter_conds):
        return exp_attr_names, exp_attr_vals, ''

    @classmethod
    def query_loop_for_limit(self, option, target_count, pager_key, pager_keys, use_cate_filter=False):
        items_all = []
        loop_count = 0
        loop_count_max = 5
        need_count = target_count

        while loop_count < loop_count_max:
            adjust_count = self.get_adjust_count(need_count, use_cate_filter)
            option['Limit'] = need_count + adjust_count
            if pager_key:
                option['ExclusiveStartKey'] = pager_key

            items, pager_key = self.exe_query(option)

            is_break = False
            if len(items) < need_count and pager_key:
                need_count = need_count - len(items)
            else:
                is_break = True

            items_all.extend(items)

            if is_break:
                break

            loop_count += 1

        if len(items_all) > target_count:
            items_all = items_all[:target_count]
            pager_key = self.get_pager_key_from_list(items_all, pager_keys['pkey'],
                                                     pager_keys['index_pkey'], pager_keys['index_skey'])

        return items_all, pager_key

    @classmethod
    def exe_query(self, option):
        table = self.get_table()
        res = table.query(**option)
        return res.get('Items', []), res.get('LastEvaluatedKey')

    @staticmethod
    def get_adjust_count(required_count, use_cate_filter=False):
        if use_cate_filter:
            if required_count < 10:
                adjust_count = 50
            elif required_count < 50:
                adjust_count = 100
            else:
                adjust_count = 300
        else:
            if required_count < 10:
                adjust_count = 20
            elif required_count < 50:
                adjust_count = 50
            else:
                adjust_count = 100

        return adjust_count

    @staticmethod
    def get_pager_key_from_list(items, pkey, index_pkey, index_skey):
        item = items[-1]
        return {
            pkey: item[pkey],
            index_pkey: item[index_pkey],
            index_skey: item[index_skey],
        }


class ModelInvalidParamsException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
