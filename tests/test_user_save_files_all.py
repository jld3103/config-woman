import subprocess

import yaml


def test_files():
    with open('/root/test.txt', 'w') as file:
        file.write('bla')
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'files': {'test.txt': '0:0:644'}}))
    subprocess.run(['python', 'main.py', 'user', 'save'])
    with open('system_files/test.txt', 'r') as file:
        assert file.read() == 'bla'
