import os
import sys
import argparse
from app.common.log import init_logger
from app.models.dynamodb import Post, Category, PostTag, ModelInvalidParamsException

logger = init_logger()

parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)


class MigrateTablePostAddCategoryPath:
    def __init__(self, service_id):
        self.service_id = service_id
        self.cate_table = {}

    def __del__(self):
        pass

    def main(self):
        logger.info('Migrating table Post for serviceId: %s', self.service_id)

        self.set_cate_table()
        if not self.cate_table:
            logger.warning('No categories found')
            return

        keys = {'serviceId': self.service_id}
        params = {'count': 200}
        pager_key = None
        while True:
            if pager_key:
                params['pagerKey'] = pager_key

            res = Post.get_all_pager_new(keys, params, 'publishAtGsi', True)
            logger.info('pagerKey %s', pager_key)
            if not res.get('items') or len(res['items']) == 0:
                logger.info('No items found')
                break

            for post in res['items']:
                cate_path = self.cate_table.get(post['categorySlug'], '')
                publish_at = post['publishAt']

                status = post['postStatus']
                is_publish = status == 'publish'
                is_hidden = post.get('isHiddenInList', False)

                sort_key_prefix, publish_at_key = Post.get_sort_key_items(
                    is_publish, is_hidden, publish_at)

                attr_items = [sort_key_prefix, publish_at_key]
                status_publish_at = '#'.join(attr_items)

                attr_items = [sort_key_prefix, cate_path, publish_at_key]
                status_cate_path = '_'.join(attr_items)

                try:
                    upd_keys = {'postId': post['postId']}
                    upd_vals = {
                        'categoryPath': cate_path,
                        'statusPublishAt': status_publish_at,
                        'statusCategoryPathPublishAt': status_cate_path,
                    }
                    upd_post = Post.update_new(upd_keys, upd_vals)
                    logger.info('Updated post: %s', upd_post['postId'])

                    self.update_post_tags(
                        upd_post['postId'], status_publish_at)

                except ModelInvalidParamsException as e:
                    logger.warning('Failed to create item: %s', e)
                except Exception as e:
                    logger.warning('Failed to create item: %s', e)

            if not res.get('pagerKey'):
                break
            pager_key = res['pagerKey']

    def update_post_tags(self, post_id, status_publish_at):
        post_tag_keys = {'postId': post_id}
        post_tags = PostTag.get_all_new(post_tag_keys)
        if not post_tags:
            return

        for post_tag in post_tags:
            tag_id = post_tag['tagId']
            self.update_post_tag_status(post_id, tag_id, status_publish_at)
            logger.info('Updated post_tag: %s-%s', post_id, tag_id)

    def update_post_tag_status(self, post_id, tag_id, status_publish_at):
        keys = {'postId': post_id, 'tagId': tag_id}
        upd_vals = {'statusPublishAt': status_publish_at}
        new_tag = PostTag.update_new(keys, upd_vals)
        return new_tag

    def set_cate_table(self):
        logger.info('Setting category table for serviceId: %s',
                    self.service_id)
        keys = {'serviceId': self.service_id}
        params = {'count': 200}
        cates = Category.get_all_new(keys, params, 'gsi-list-by-service', True)
        if not cates:
            logger.info('No categories found')
            return

        for cate in cates:
            path_items = [cate['parentPath'], str(cate['id'])]
            cate_path = '#'.join(path_items)
            slug = cate['slug']
            self.cate_table[slug] = cate_path


# Usage:
# python app/bin/migrate_table_post_add_category_path.py service-id


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('service_id', help="Service ID for copy")
    args = parser.parse_args()
    copier = MigrateTablePostAddCategoryPath(args.service_id)
    copier.main()
