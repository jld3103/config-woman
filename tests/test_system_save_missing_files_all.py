import os
import subprocess

import yaml


def test_missing():
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) > 0

    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        default_missing_count = len(document['files'])
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'files': {'/etc/shadow': '0:0:600'}}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == default_missing_count - 1

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    with open('/etc/test.txt', 'w') as file:
        file.write('bla')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1
    os.remove('/etc/test.txt')

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_missing.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'exclude_files': ['/etc/shadow']}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        # Ubuntu does not have /etc/shadow-, so it is only one file less instead of the expected two on other
        # distributions
        assert len(document['files']) < default_missing_count
