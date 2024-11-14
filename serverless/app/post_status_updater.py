from app.common.log import init_logger
from app.models.dynamodb import Service, Post, PostTag, ModelInvalidParamsException

logger = init_logger()


def handler(event=None, context=None):
    logger.info('START: post_status_updater.handler')
    logger.info('post_status_update.handler: event: %s', event)

    try:
        updater = PostStatusUpdater()
        updater.main()
        logger.info('END: post_status_updater.handler')
        return 'Success'

    except Exception as e:
        logger.exception('post_status_updater.handler: Error: %s', e)


class PostStatusUpdater:
    def __init__(self):
        pass

    def main(self):
        services = Service.scan_all()
        for service in services:
            self.update_posts_status_by_service(service['serviceId'])

    def update_posts_status_by_service(self, service_id):
        keys = {
            'serviceId': service_id,
            'statusPublishAt': 'reserve'
        }
        params = {'count': 200, 'order': 'asc'}
        posts = Post.get_all_new(
            keys, params, 'statusPublishAtGsi', True, 'begins_with')
        for post in posts:
            post_id = post['postId']
            upd_post = self.update_post_status(post)
            if not upd_post:
                continue
            logger.info('Updated post: %s', post_id)

            post_tag_keys = {'postId': post_id}
            post_tags = PostTag.get_all_new(post_tag_keys)
            if not post_tags:
                continue

            for post_tag in post_tags:
                tag_id = post_tag['tagId']
                self.update_post_tag_status(
                    post_id, tag_id, upd_post['statusPublishAt'])
                logger.info('Updated post_tag: %s-%s', post_id, tag_id)

    def update_post_status(self, post):
        publish_at = post.get('publishAt')
        is_publish = post['postStatus'] == 'publish'
        is_hidden = post.get('isHiddenInList', False)
        sort_key_prefix, publish_at_key = Post.get_sort_key_items(
            is_publish, is_hidden, publish_at)
        if sort_key_prefix == 'reserve':
            return

        attr_items = [sort_key_prefix, publish_at_key]
        status_publish_at = '#'.join(attr_items)

        cate_path = post.get('categoryPath', '')
        attr_items = [sort_key_prefix, cate_path, publish_at_key]
        status_cate_path = '_'.join(attr_items)

        post_id = post['postId']
        try:
            upd_keys = {'postId': post_id}
            upd_vals = {
                'statusPublishAt': status_publish_at,
                'statusCategoryPathPublishAt': status_cate_path,
            }
            upd_post = Post.update_new(upd_keys, upd_vals)
            return upd_post
        except ModelInvalidParamsException as e:
            logger.exception('ModelInvalidParamsException: %s', e)
        except Exception as e:
            logger.exception('Failed to update item: %s', e)

    def update_post_tag_status(self, post_id, tag_id, status_publish_at):
        keys = {'postId': post_id, 'tagId': tag_id}
        upd_vals = {'statusPublishAt': status_publish_at}
        new_tag = PostTag.update_new(keys, upd_vals)
        return new_tag
