import os
import subprocess

import yaml


def test_missing():
    with open('/root/.123', 'w') as file:
        file.write('bla')
    with open('/root/.test', 'w') as file:
        file.write('bla')

    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) > 0

    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        default_missing_count = len(document['files'])
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'files': {'.test': '0:0:644'}}))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == default_missing_count - 1

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    with open('/root/.bla', 'w') as file:
        file.write('test')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == 1
    os.remove('/root/.bla')

    os.remove('system.yaml')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    assert not os.path.exists('system_missing.yaml')

    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'exclude_files': ['/root/.test']}))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_missing.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['files']) == default_missing_count - 1
