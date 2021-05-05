import os
import subprocess

import yaml

from helpers import get_system_package_manager


def common_redundant_packages(package):
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'packages': ['idonotexist']}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['packages']) == 1

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'packages': []}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    get_system_package_manager().install_packages([package], True)
    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    get_system_package_manager().remove_packages([package], True)
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['packages']) == 1
