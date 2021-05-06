import os
import subprocess

import yaml

from helpers import get_system_package_manager


def common_apply(package):
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')

    previous_packages = get_system_package_manager().get_packages()
    assert package not in previous_packages

    with open('system.yaml', 'w') as file:
        packages = previous_packages.copy()
        packages.append(package)
        file.write(yaml.dump({'mode': 'system', 'packages': packages}))
    subprocess.run(['python', 'main.py', 'system', 'apply', '--no-confirm'])
    new_packages = get_system_package_manager().get_packages()
    assert len(new_packages) == len(previous_packages) + 1
    assert package in new_packages

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'system', 'packages': previous_packages}))

    subprocess.run(['python', 'main.py', 'system', 'apply', '--no-confirm'])
    new_packages = get_system_package_manager().get_packages()
    assert len(new_packages) == len(previous_packages)
    assert package not in new_packages
