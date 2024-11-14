import os
import sys
import argparse
from app.common.log import init_logger
from app.common.dynamodb_handler import DynamoDBHandler
from app.models.dynamodb import VoteCount, ModelInvalidParamsException

logger = init_logger()

parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)


class DynamoDBVoteCountItemsCopier:
    def __init__(self, service_id, from_table_prefix, is_copy_from_local_table=False):
        self.service_id = service_id
        self.from_db = DynamoDBHandler(
            from_table_prefix, is_copy_from_local_table)

    def __del__(self):
        pass

    def main(self):
        pager_key = None
        table_name = VoteCount.table_name
        while True:
            params = {'pagerKey': pager_key} if pager_key else None
            res = self.from_db.get_all_pager(
                table_name, {'serviceId': self.service_id}, params)
            if not res.get('items'):
                break
            for item in res['items']:
                keys = {
                    'serviceId': self.service_id,
                    'contentIdType': item['contentIdType'],
                }
                vals = VoteCount.get_one_by_pkey_new(keys, True, True)
                if vals:
                    logger.info('Item already exists: %s', keys)
                    continue
                try:
                    logger.info('Creating item for keys: %s, vals: %s',
                                keys, item)
                    created = VoteCount.create(item)
                    logger.info('Created item: %s', created)
                except ModelInvalidParamsException as e:
                    logger.warning('Failed to create item: %s', e)
                except Exception as e:
                    logger.warning('Failed to create item: %s', e)

            pager_key = res.get('pagerKey')
            if not pager_key:
                break

# Usage:
# python app/bin/dynamo_db_vote_count_items_copier.py service-id your-prj-prd


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('service_id', help="Service ID for copy")
    parser.add_argument('from_table_prefix',
                        help="Table name prefix for copy from")
    parser.add_argument('--local-table-from', '-l', required=False,
                        type=bool, default=False, help="If you want to copy from local table, set True")
    args = parser.parse_args()
    copier = DynamoDBVoteCountItemsCopier(
        args.service_id, args.from_table_prefix, args.local_table_from)
    copier.main()
