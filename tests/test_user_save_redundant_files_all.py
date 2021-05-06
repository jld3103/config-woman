import os
import subprocess

import yaml


def test_redundant():
    subprocess.run(['python', 'main.py', 'user', 'save'])
    assert not os.path.exists('system_redundant.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'files': {'.test': '0:0:644'}}))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1

    with open('/root/.test', 'w') as file:
        file.write('bla')
    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    os.remove('/root/.test')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1
