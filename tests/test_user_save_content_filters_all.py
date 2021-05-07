import os
import subprocess

import yaml


def test_content_filters():
    with open('/root/.123', 'w') as file:
        file.write('bla\ndef\nghi')

    subprocess.run(['python', 'main.py', 'user', 'save'])
    os.rename('system_missing.yaml', 'system.yaml')
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_files/.123', 'r') as file:
        assert 'def' in file.read()

    with open('system.yaml', 'r') as file:
        document = yaml.load(file.read(), Loader=yaml.FullLoader)
    document['content_filters'] = [{'.123': 'def'}]
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump(document))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_files/.123', 'r') as file:
        assert 'def' not in file.read()
