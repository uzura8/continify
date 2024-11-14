import os
import sys
from app.post_status_updater import PostStatusUpdater
from app.common.log import init_logger

logger = init_logger()

parent_dir = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)


class TestPostStatusUpdater:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def main(self):
        post_status_updater = PostStatusUpdater()
        post_status_updater.main()


if __name__ == '__main__':
    test_handler = TestPostStatusUpdater()
    test_handler.main()
