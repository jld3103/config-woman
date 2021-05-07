import os
import subprocess

import yaml


def test_content_filters():
    subprocess.run(['python', 'main.py', 'system', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_files/etc/shadow', 'r') as file:
        assert 'nobody' in file.read()

    with open('system.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
    document['content_filters'] = [{'/etc/shadow': 'nobody.*'}]
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump(document))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('system_files/etc/shadow', 'r') as file:
        assert 'nobody' not in file.read()
