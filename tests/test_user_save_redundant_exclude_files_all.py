import os
import subprocess

import yaml


def test_redundant():
    subprocess.run(['python', 'main.py', 'user', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'exclude_files': ['.test']}))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['exclude_files']) == 1
