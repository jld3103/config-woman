import os
import subprocess

import yaml

from package_manager.utils import get_system_package_manager


def common_missing(package1, package2):
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['packages']) > 0

    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        default_missing_count = len(document['packages'])
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'packages': [package1]}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['packages']) == default_missing_count - 1

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    get_system_package_manager().install_packages([package2], True)
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['packages']) == 1

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_missing.yaml')
