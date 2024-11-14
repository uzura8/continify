import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_base_dir = os.path.join(BASE_DIR, '../config/')


def load_config(config_file_sub_path):
    config_file_path = os.path.join(config_base_dir, config_file_sub_path)
    with open(config_file_path, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None

