import os

import yaml


def load_system_config(config_directory):
    file_path = os.path.join(config_directory, 'system.yaml')
    if not os.path.exists(file_path):
        if not os.path.exists(config_directory):
            os.makedirs(config_directory)
        # Create an empty file to start with
        with open(file_path, 'w') as file:
            file.write(yaml.dump({'packages': []}, default_flow_style=False))
        return Config([])
    with open(file_path, 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        packages = []
        for package in document['packages']:
            packages.append(package)
        return Config(packages=packages)


def write_missing_system_config(config_directory, missing_config):
    file_path = os.path.join(config_directory, 'system_missing.yaml')
    with open(file_path, 'w') as file:
        file.write(yaml.dump({'packages': missing_config.packages}, default_flow_style=False))


def write_redundant_system_config(config_directory, redundant_config):
    file_path = os.path.join(config_directory, 'system_redundant.yaml')
    with open(file_path, 'w') as file:
        file.write(yaml.dump({'packages': redundant_config.packages}, default_flow_style=False))


class Config:
    def __init__(self, packages: [str]):
        self.packages = packages
