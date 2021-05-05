import os
import subprocess

import yaml


def test_redundant():
    subprocess.run(['python', 'main.py', 'system', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'exclude_files': ['/etc/test.txt']}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['exclude_files']) == 1
