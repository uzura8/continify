import os
import sys
import argparse
from app.common.log import init_logger
from app.common.dynamodb_handler import DynamoDBHandler
from app.models.dynamodb import ShortenUrl, ModelInvalidParamsException

PARAM_VAL_PREFIX = 'qr'
DEFAULT_ASSIGNEE_NAME = 'データ移行項目のため、不明'

logger = init_logger()

parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)


class DynamoDBShortenUrlItemsCopier:
    def __init__(self, from_service_id, to_service_id, from_table_prefix, is_copy_from_local_table=False):
        self.from_service_id = from_service_id
        self.to_service_id = to_service_id
        self.from_db = DynamoDBHandler(
            from_table_prefix, is_copy_from_local_table)

    def __del__(self):
        pass

    def main(self):
        pager_key = None
        table_name = ShortenUrl.table_name
        while True:
            params = {'pagerKey': pager_key} if pager_key else None
            res = self.from_db.get_all_pager(
                table_name, {'serviceId': self.from_service_id}, params, 'createdAtGsi')
            if not res.get('items'):
                break
            for item in res['items']:
                vals = self.convert_old_item_to_new(item)
                try:
                    res = ShortenUrl.create_item(vals, PARAM_VAL_PREFIX)
                    logger.info('Created item: %s', res)
                except ModelInvalidParamsException as e:
                    logger.warning('Failed to create item: %s', e)

            pager_key = res.get('pagerKey')
            if not pager_key:
                break

    def convert_old_item_to_new(self, old_item):
        vals = {} | old_item
        vals['serviceId'] = self.to_service_id
        vals['assigneeName'] = DEFAULT_ASSIGNEE_NAME
        vals['assigneeMemo'] = ''
        vals['confirmStatus'] = 'confirmed'
        vals['confirmStatusCreatedAt'] = f"confirmed#{vals['createdAt']}"
        vals['confirmedAt'] = vals['updatedAt'] if vals.get(
            'updatedAt') else vals['createdAt']
        vals['urlCreatedAt'] = '|'.join(
            [vals['url'], vals['createdAt']])
        return vals


# Usage:
# python app/bin/dynamo_db_shorten_url_items_copier.py service-id-from service-id-to your-prj-prd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('from_service_id', help="Service ID for copy from")
    parser.add_argument('to_service_id', help="Service ID for copy to")
    parser.add_argument('from_table_prefix',
                        help="Table name prefix for copy from")
    parser.add_argument('--local-table-from', '-l', required=False,
                        type=bool, default=False, help="If you want to copy from local table, set True")
    args = parser.parse_args()
    copier = DynamoDBShortenUrlItemsCopier(
        args.from_service_id, args.to_service_id, args.from_table_prefix, args.local_table_from)
    copier.main()
