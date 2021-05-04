import os

import yaml


def load_system_config(config_directory, preset):
    file_path = os.path.join(config_directory, f'{preset}.yaml')
    if not os.path.exists(file_path):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)
        # Create an empty file to start with
        with open(file_path, 'w') as file:
            file.write(yaml.dump({'packages': [], 'files': {}, 'exclude_files': []}, default_flow_style=False))
        return Config([], [], [])
    with open(file_path, 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        packages = []
        files = {}
        exclude_files = []
        if 'packages' in document:
            packages = document['packages']
        if 'files' in document:
            for path in document['files']:
                files[path] = document['files'][path]
        if 'exclude_files' in document:
            exclude_files = document['exclude_files']
        return Config(packages, files, exclude_files)


def write_missing_system_config(config_directory, preset, missing_config):
    file_path = os.path.join(config_directory, f'{preset}_missing.yaml')
    _write_system_config(file_path, missing_config)


def write_redundant_system_config(config_directory, preset, redundant_config):
    file_path = os.path.join(config_directory, f'{preset}_redundant.yaml')
    _write_system_config(file_path, redundant_config)


def _write_system_config(file_path, config):
    if len(config.packages) > 0 or len(config.files) > 0 or len(config.exclude_files) > 0:
        with open(file_path, 'w') as file:
            file.write(yaml.dump({
                'packages': config.packages,
                'files': config.files,
                'exclude_files': config.exclude_files,
            }, default_flow_style=False))
    elif os.path.exists(file_path):
        os.remove(file_path)


class Config:
    def __init__(self, packages: [str], files: {}, exclude_files: [str]):
        self.packages = packages
        self.files = files
        self.exclude_files = exclude_files
