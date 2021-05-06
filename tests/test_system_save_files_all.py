import subprocess

import yaml


def test_files():
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'system', 'files': {'/etc/shadow': '0:0:600'}}))
    subprocess.run(['python', 'main.py', 'system', 'save'])
    with open('/etc/shadow', 'r') as original_file:
        with open('system_files/etc/shadow', 'r') as copied_file:
            assert copied_file.read() == original_file.read()
