import os
import subprocess

import yaml


def test_redundant():
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_files/etc/shadow', 'r') as file:
        assert '123456' not in file.read()

    with open('system.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
    document['content_filters'] = [{'/etc/shadow': '123456'}]
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump(document))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_files/etc/shadow', 'r') as file:
        assert '123456' not in file.read()
    with open('system_redundant.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
        assert len(document['content_filters']) == 1
