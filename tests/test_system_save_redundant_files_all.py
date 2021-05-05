import os
import subprocess

import yaml


def test_redundant():
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'files': {'/etc/test.txt': '0:0:644'}}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1

    with open('/etc/test.txt', 'w') as file:
        file.write('bla')
    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    os.remove('/etc/test.txt')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1
