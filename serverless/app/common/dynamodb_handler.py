import boto3


class DynamoDBHandler:

    def __init__(self, prefix, is_local=False):
        self.dynamodb = None
        self.prefix = prefix
        self.connect_dynamodb(is_local)

    def connect_dynamodb(self, is_local=False):
        if is_local:
            self.dynamodb = boto3.resource(
                'dynamodb', endpoint_url='http://localhost:8000')
        else:
            self.dynamodb = boto3.resource('dynamodb')

    def get_table_name(self, table_name):
        return '-'.join([self.prefix, table_name])

    def get_table(self, table_name):
        table = self.get_table_name(table_name)
        return self.dynamodb.Table(table)

    def scan(self, table_name, exclusive_start_key=None):
        table = self.get_table(table_name)
        scan_kwargs = {}
        if exclusive_start_key:
            scan_kwargs['ExclusiveStartKey'] = exclusive_start_key
        response = table.scan(**scan_kwargs)
        return response

    def get_one_by_pkey(self, table_name, keys, consistent_read=False):
        table = self.get_table(table_name)
        get_item_kwargs = {'Key': keys}
        if consistent_read:
            get_item_kwargs['ConsistentRead'] = True
        res = table.get_item(**get_item_kwargs)
        item = res.get('Item')
        return item if item else None

    def get_all_pager(self, table_name, keys, params=None, index=None, skey_cond_type='eq'):
        """
        params = {
            'order': 'asc' or 'desc',
            'count': number,
            'pagerKey': {},
        }
        """
        table = self.get_table(table_name)

        is_desc = False
        limit = 200
        if params:
            is_desc = params.get('order', 'asc') == 'desc'
            limit = params.get('count', 200)
        option = {
            'ScanIndexForward': not is_desc,
        }
        if limit:
            option['Limit'] = limit

        if params and params.get('pagerKey'):
            option['ExclusiveStartKey'] = params['pagerKey']

        if index:
            option['IndexName'] = index

        if not isinstance(keys, dict) or len(keys) == 0:
            raise ValueError("keys must not be empty")
        elif len(keys) == 1:
            pkey, pval = next(iter(keys.items()))
            skey, sval = None, None
        else:
            items = list(keys.items())
            pkey, pval = items[0]
            skey, sval = items[1]

        key_cond_exps = ['#pk = :pk']
        exp_attr_names = {'#pk': pkey}
        exp_attr_vals = {':pk': pval}

        if all([skey, sval]):
            exp_attr_names['#sk'] = skey
            exp_attr_vals[':sk'] = sval
            if skey_cond_type == 'begins_with':
                key_cond_exps.append('begins_with(#sk, :sk)')
            else:
                key_cond_exps.append('#sk = :sk')

        option['KeyConditionExpression'] = ' AND '.join(key_cond_exps)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        res = table.query(**option)
        items = res.get('Items', [])
        pager_key = res.get('LastEvaluatedKey')
        return {'items': items, 'pagerKey': pager_key}
