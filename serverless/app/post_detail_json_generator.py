import json
import os
from app.aws_s3_handler import AwsS3Handler
from app.common.log import init_logger
from app.common.date import is_future, utc_iso
from app.common.dict import check_same_dicts
from app.common.decimal_encoder import DecimalEncoder
from app.models.dynamodb import Post

MEDIA_S3_BUCKET_NAME = os.environ.get('MEDIA_S3_BUCKET_NAME')
MEDIA_DISTRIBUTION_ID = os.environ.get('MEDIA_DISTRIBUTION_ID')
# DEBUG_LOG_ENABLED = os.environ.get('DEBUG_LOG_ENABLED') == 'true'

logger = init_logger()


class PostDetailJsonGenerator:
    s3handler = None
    bucket_dir_path = ''
    # debug_log_enabled = False
    url_shorten_base_url = ''

    def __init__(self):
        # self.debug_log_enabled = DEBUG_LOG_ENABLED
        self.s3handler = AwsS3Handler(
            MEDIA_S3_BUCKET_NAME, MEDIA_DISTRIBUTION_ID)

    def __del__(self):
        pass

    def create_json(self, post_event_data):
        post_id = get_val(post_event_data, 'postId', 'S')
        item = Post.get_one_by_pkey_new({'postId': post_id}, True, True)
        if not item:
            raise InvalidValueError('postId does not exist | %s' % post_id)

        if item['postStatus'] == 'unpublish':
            raise InvalidValueError('postId is unpublish | %s' % post_id)

        if is_future(item['publishAt']):
            raise InvalidValueError('postId is future | %s' % post_id)

        json_data = json.dumps(Post.to_response(item), cls=DecimalEncoder)
        object_key = self.generate_object_key(item['serviceId'], item['slug'])
        self.s3handler.upload(json_data, object_key, 'application/json')
        # self.update_post_cache_status(post_id, True)
        logger.info(
            'post_detail_json_generator.create_json: json created | %s', object_key)

    def remove_json(self, post_event_data, is_update_cache_status=False):
        service_id = get_val(post_event_data, 'serviceId', 'S')
        slug = get_val(post_event_data, 'slug', 'S')
        object_key = self.generate_object_key(service_id, slug)
        self.s3handler.delete(object_key)
        # if is_update_cache_status:
        #     post_id = get_val(post_event_data, 'postId', 'S')
        #     self.update_post_cache_status(post_id, False)
        logger.info(
            'post_detail_json_generator.remove_json: json removed | %s', object_key)

    # @staticmethod
    # def update_post_cache_status(post_id, is_created):
    #     vals = {'isS3CacheCreated': is_created}
    #     if is_created:
    #         vals['s3CacheCreatedAt'] = utc_iso(False, True)
    #     else:
    #         vals['s3CacheCreatedAt'] = None
    #     Post.update(post_id, vals, False)

    @staticmethod
    def generate_object_key(service_id, slug):
        return f'posts/{service_id}/{slug}.json'


def get_val(target_dict, attr_name, data_type):
    try:
        res = target_dict[attr_name][data_type]
        return res
    except KeyError:
        return None


def get_event_item(events, is_new_image=True):
    image_key = 'NewImage' if is_new_image else 'OldImage'
    return events['dynamodb'][image_key]


class InvalidValueError(Exception):
    pass


def handler(event=None, context=None):
    logger.info('START: post_detail_json_generator.handler')
    logger.info('event: %s', event)

    generator = PostDetailJsonGenerator()
    if event and 'Records' in event:
        err_cnt = 0
        for r in event['Records']:
            if r['eventName'] not in ['INSERT', 'MODIFY', 'REMOVE']:
                logger.info(
                    'Skipped: eventName is not INSERT or MODIFY or REMOVE')
                continue

            try:
                if r['eventName'] == 'INSERT':
                    new_image = get_event_item(r)
                    post_id = get_val(new_image, 'postId', 'S')

                    publish_status_new = get_val(new_image, 'postStatus', 'S')
                    if publish_status_new == 'unpublish':
                        logger.info(
                            'Skipped: postStatus is unpublish | postId: %s', post_id)
                        continue

                    publish_at_new = get_val(new_image, 'publishAt', 'S')
                    if is_future(publish_at_new):
                        logger.info(
                            'Skipped: publishAt is future | postId: %s', post_id)
                        continue

                    generator.create_json(new_image)

                elif r['eventName'] == 'MODIFY':
                    old_image = get_event_item(r, False)
                    new_image = get_event_item(r)
                    post_id = get_val(new_image, 'postId', 'S')

                    # # キャッシュ関連以外の変更がない場合はスキップ
                    # if check_same_dicts(new_image, old_image, ['isS3CacheCreated', 's3CacheCreatedAt']):
                    #     logger.info(
                    #         'Skipped: No change in items | postId: %s', post_id)
                    #     continue

                    # 非公開に変更された場合は削除
                    publish_status_old = get_val(old_image, 'postStatus', 'S')
                    publish_status_new = get_val(new_image, 'postStatus', 'S')
                    if publish_status_new != publish_status_old:
                        if publish_status_new == 'unpublish':
                            logger.info(
                                'Removed: postStatus is unpublish | postId: %s', post_id)
                            generator.remove_json(old_image, True)
                            continue

                    # 公開日時が未来に変更された場合は削除
                    publish_at_old = get_val(old_image, 'publishAt', 'S')
                    publish_at_new = get_val(new_image, 'publishAt', 'S')
                    if publish_at_new != publish_at_old:
                        if is_future(publish_at_new):
                            logger.info(
                                'Removed: publishAt is future | postId: %s', post_id)
                            generator.remove_json(old_image, True)
                            continue

                    # slugが変更された場合は削除して再作成
                    slug_old = get_val(old_image, 'slug', 'S')
                    slug_new = get_val(new_image, 'slug', 'S')
                    if slug_new != slug_old:
                        logger.info(
                            'Removed: slug changed | postId: %s', post_id)
                        generator.remove_json(old_image)

                    generator.create_json(new_image)

                elif r['eventName'] == 'REMOVE':
                    post_event_data = get_event_item(r, False)
                    generator.remove_json(post_event_data)

            except Exception as e:
                # tb = sys.exc_info()[2]
                # msg = e.with_traceback(tb)
                # output_log(msg, 'error')
                logger.error(e, exc_info=True)
                err_cnt += 1

        return 'Success' if not err_cnt else 'END: post_detail_json_generator.handler: Error'
