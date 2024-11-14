from app.common.date import utc_iso
from app.common.string import new_uuid
from app.models.dynamodb import Base, ModelInvalidParamsException
from app.models.dynamodb.service import Service
from app.models.dynamodb.comment_count import CommentCount


class Comment(Base):
    table_name = 'comment'
    public_attrs = [
        'commentId',
        'contentId',
        'createdAt',
        'body',
        'profiles',
        'serviceId',
        'serviceIdContentId',
        'statusCreatedAt',
        'publishStatus',
    ]
    response_attrs = public_attrs + []
    private_attrs = [
        'ip',
        'ua',
    ]
    all_attrs = public_attrs + private_attrs

    allowed_vals = {
        'publishStatus': ['publish', 'unpublish'],
    }

    reserved_values = {
        'commentId': ['all']
    }

    @classmethod
    def query_all_publish(self, service_id, content_id, params, is_public=True):
        index_name = 'commentStatusCreatedAtGsi'
        table = self.get_table()
        until_time = params.get('untilTime', '')
        since_time = params.get('sinceTime', '')
        is_desc = params.get('order', 'asc') == 'desc'
        limit = params.get('count', 10)

        sort_key = 'createdAt'
        exp_attr_names = {}
        exp_attr_vals = {}
        key_conds = ['#si = :si']
        option = {
            'IndexName': index_name,
            'ScanIndexForward': not is_desc,
            'Limit': limit,
            'ProjectionExpression': self.prj_exps_str(is_public),
        }
        exp_attr_names['#si'] = 'serviceIdContentId'
        exp_attr_vals[':si'] = '#'.join([service_id, content_id])

        key_conds.append('begins_with(#sp, :sp)')
        exp_attr_names['#sp'] = 'statusCreatedAt'
        exp_attr_vals[':sp'] = 'publish'

        filter_exps = []
        if since_time:
            cond = '#st > :st'
            exp_attr_names['#st'] = sort_key
            exp_attr_vals[':st'] = since_time
            filter_exps.append(cond)

        if until_time:
            cond = '#ut < :ut'
            exp_attr_names['#ut'] = sort_key
            exp_attr_vals[':ut'] = until_time
            filter_exps.append(cond)

        filter_exps_str = ' AND '.join(filter_exps) if filter_exps else ''

        filter_exp = ''
        if filter_exps_str:
            filter_exp += filter_exps_str

        if filter_exp:
            option['FilterExpression'] = filter_exp
            option['Limit'] += 500

        option['KeyConditionExpression'] = ' AND '.join(key_conds)
        option['ExpressionAttributeNames'] = exp_attr_names
        option['ExpressionAttributeValues'] = exp_attr_vals
        result = table.query(**option)
        items = result.get('Items', [])[:limit]

        return items

    @classmethod
    def create_and_count_up(self, vals, is_return_all_attrs=False):
        service_id = vals.get('serviceId')
        content_id = vals.get('contentId')
        publish_status = vals.get('publishStatus')
        if any([not service_id, not content_id, not publish_status]):
            raise ModelInvalidParamsException(
                'serviceId, contentId, publishStatus are required')
        self.check_set_reserved_value(vals)

        time = utc_iso(False, True)

        comment_id = new_uuid()
        comment_vals = vals | {
            'commentId': comment_id,
            'createdAt': time,
            'serviceIdContentId': '#'.join([service_id, content_id]),
            'statusCreatedAt': '#'.join([publish_status, time]),
        }
        count_keys = {
            'serviceId': service_id,
            'contentIdPublishStatus': '#'.join([content_id, publish_status]),
        }
        count_add_vals = {'commentCount': 1}
        count_upd_vals = {'updatedAt': time}
        count_options = self.get_count_up_and_update_options(
            count_keys, count_add_vals, count_upd_vals)
        count_options['TableName'] = CommentCount.get_table_name()

        dynamodb = self.connect_dynamodb()
        res = dynamodb.meta.client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': self.get_table_name(),
                        'Item': comment_vals
                    }
                },
                {
                    'Update': count_options
                }
            ]
        )
        keys = {'commentId': comment_id}
        comment = self.get_one_by_pkey_new(keys, is_return_all_attrs)
        return comment

    @classmethod
    def update_publish_status_and_count(cls, comment, new_publish_status, other_vals=None):
        comment_id = comment['commentId']
        old_publish_status = comment['publishStatus']
        service_id = comment['serviceId']
        content_id = comment['contentId']
        created_at = comment['createdAt']
        updated_at = utc_iso(False, True)

        if old_publish_status == new_publish_status:
            raise ModelInvalidParamsException(
                "Publish status is the same as the current status")

        old_count_keys = {
            'serviceId': service_id,
            'contentIdPublishStatus': '#'.join([content_id, old_publish_status]),
        }
        new_count_keys = {
            'serviceId': service_id,
            'contentIdPublishStatus': '#'.join([content_id, new_publish_status]),
        }

        # Reduce comment count
        count_sub_vals = {'commentCount': -1}
        count_upd_vals = {'updatedAt': updated_at}
        old_count_options = cls.get_count_up_and_update_options(
            old_count_keys, count_sub_vals, count_upd_vals
        )
        old_count_options['TableName'] = CommentCount.get_table_name()

        # Increase comment count
        count_add_vals = {'commentCount': 1}
        new_count_options = cls.get_count_up_and_update_options(
            new_count_keys, count_add_vals, count_upd_vals
        )
        new_count_options['TableName'] = CommentCount.get_table_name()

        # Update comment
        update_comment_vals = {
            'publishStatus': new_publish_status,
            'statusCreatedAt': '#'.join([new_publish_status, created_at]),
            'updatedAt': updated_at,
        } | (other_vals or {})

        update_comment_options = {
            'TableName': cls.get_table_name(),
            'Key': {'commentId': comment_id},
            'UpdateExpression': 'SET publishStatus = :ps, statusCreatedAt = :sca, updatedAt = :ua',
            'ExpressionAttributeValues': {
                ':ps': new_publish_status,
                ':sca': update_comment_vals['statusCreatedAt'],
                ':ua': update_comment_vals['updatedAt'],
            }
        }

        # Execute transaction
        dynamodb = cls.connect_dynamodb()
        res = dynamodb.meta.client.transact_write_items(
            TransactItems=[
                {
                    'Update': old_count_options
                },
                {
                    'Update': new_count_options
                },
                {
                    'Update': update_comment_options
                }
            ]
        )

        # Get updated comment
        updated_comment = cls.get_one_by_pkey_new(
            {'commentId': comment_id}, True, True)
        return updated_comment

    @classmethod
    def delete_and_count_down(cls, comment):
        comment_id = comment['commentId']
        service_id = comment['serviceId']
        content_id = comment['contentId']
        publish_status = comment['publishStatus']
        time = utc_iso(False, True)

        count_keys = {
            'serviceId': service_id,
            'contentIdPublishStatus': '#'.join([content_id, publish_status]),
        }
        count_sub_vals = {'commentCount': -1}
        count_upd_vals = {'updatedAt': time}
        count_options = cls.get_count_up_and_update_options(
            count_keys, count_sub_vals, count_upd_vals)
        count_options['TableName'] = CommentCount.get_table_name()

        comment_options = {
            'TableName': cls.get_table_name(),
            'Key': {'commentId': comment_id},
        }

        dynamodb = cls.connect_dynamodb()
        res = dynamodb.meta.client.transact_write_items(
            TransactItems=[
                {
                    'Update': count_options
                },
                {
                    'Delete': comment_options
                }
            ]
        )
        return True

    @classmethod
    def create_comment(self, vals):
        service_id = vals.get('serviceId')
        if not service_id:
            raise ModelInvalidParamsException('serviceId is required')

        # if not Service.check_exists(service_id):
        #    raise ModelInvalidParamsException('serviceId not exists')

        if not vals.get('commentId'):
            vals['commentId'] = new_uuid()

        if not vals.get('createdAt'):
            vals['createdAt'] = utc_iso(False, True)
        time = vals['createdAt']

        required_attrs = ['contentId']
        for attr in required_attrs:
            if attr not in vals or len(vals[attr].strip()) == 0:
                raise ModelInvalidParamsException(
                    "Argument '%s' requires values" % attr)
        content_id = vals['contentId']

        status = vals['publishStatus']
        table = self.get_table()
        item = {
            'commentId': vals['commentId'],
            'serviceId': service_id,
            'contentId': content_id,
            'serviceIdContentId': '#'.join([service_id, content_id]),
            'createdAt': vals['createdAt'],
            'body': vals['body'],
            'profiles': vals['profiles'] if vals.get('profiles') else None,
            'publishStatus': status,
            'statusCreatedAt': '#'.join([status, time]),
            'ip': vals.get('ip', ''),
            'ua': vals.get('ua', ''),
        }
        table.put_item(Item=item)
        CommentCount.update_count(service_id, content_id, status, False, time)

        return item
