import logging
import os

import yaml


def load_config(mode: str, config_directory: str, preset: str):
    file_path = os.path.join(config_directory, f'{preset}.yaml')
    if not os.path.exists(file_path):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)
        # Create an empty file to start with
        with open(file_path, 'w') as file:
            if mode == 'system':
                file.write(yaml.dump({
                    'mode': mode,
                    'exclude_files': [],
                    'content_filters': {},
                    'files': {},
                    'packages': []
                },
                    default_flow_style=False, sort_keys=False))
            else:
                file.write(yaml.dump({
                    'mode': mode,
                    'exclude_files': [],
                    'content_filters': {},
                    'files': {},
                },
                    default_flow_style=False, sort_keys=False))
        return Config(mode, [], {}, [], {})
    with open(file_path, 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        if document['mode'] != mode:
            logging.fatal(
                f'Tried loading config from preset {preset} in {mode} mode, but the config file said it was '
                f'configured for {document["mode"]} mode')
            exit(1)
        packages = []
        files = {}
        content_filters = {}
        exclude_files = []
        if 'packages' in document:
            packages = document['packages']
        if 'files' in document:
            files = document['files']
        if 'content_filters' in document:
            content_filters = document['content_filters']
        if 'exclude_files' in document:
            exclude_files = document['exclude_files']
        return Config(mode, packages, files, exclude_files, content_filters)


def write_missing_config(config_directory, preset, missing_config):
    file_path = os.path.join(config_directory, f'{preset}_missing.yaml')
    _write_config(file_path, missing_config)


def write_redundant_config(config_directory, preset, redundant_config):
    file_path = os.path.join(config_directory, f'{preset}_redundant.yaml')
    _write_config(file_path, redundant_config)


def _write_config(file_path, config):
    data = {'mode': config.mode}
    if len(config.exclude_files) > 0:
        data['exclude_files'] = config.exclude_files
    if len(config.content_filters) > 0:
        data['content_filters'] = config.content_filters
    if len(config.files) > 0:
        data['files'] = config.files
    if len(config.packages) > 0:
        data['packages'] = config.packages
    if len(data) > 1:
        with open(file_path, 'w') as file:
            file.write(yaml.dump(data, default_flow_style=False, sort_keys=False))
    elif os.path.exists(file_path):
        os.remove(file_path)


class Config:
    def __init__(self, mode: str, packages: [str], files: {}, exclude_files: [str], content_filters: []):
        self.mode = mode
        self.packages = packages
        self.files = files
        self.exclude_files = exclude_files
        self.content_filters = content_filters
