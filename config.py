import os

import yaml


def load_system_config(config_directory, preset):
    file_path = os.path.join(config_directory, '{preset}.yaml'.format(preset=preset))
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


def write_missing_system_config(config_directory, preset, missing_config):
    file_path = os.path.join(config_directory, '{preset}_missing.yaml'.format(preset=preset))
    with open(file_path, 'w') as file:
        file.write(yaml.dump({'packages': missing_config.packages}, default_flow_style=False))


def write_redundant_system_config(config_directory, preset, redundant_config):
    file_path = os.path.join(config_directory, '{preset}_redundant.yaml'.format(preset=preset))
    with open(file_path, 'w') as file:
        file.write(yaml.dump({'packages': redundant_config.packages}, default_flow_style=False))


class Config:
    def __init__(self, packages: [str]):
        self.packages = packages
