import os
import subprocess

import yaml


def test_files():
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'system', 'files': {'/etc/test.txt': '1:2:611'}}))
    os.makedirs('system_files/etc')
    with open('system_files/etc/test.txt', 'w') as file:
        file.write('bla')
    subprocess.run(['python', 'main.py', 'system', 'apply'])
    with open('system_files/etc/test.txt', 'r') as original_file:
        with open('/etc/test.txt', 'r') as copied_file:
            assert copied_file.read() == original_file.read()
            stat_info = os.stat('/etc/test.txt')
            assert stat_info.st_uid == 1
            assert stat_info.st_gid == 2
            assert stat_info.st_mode == 0o100611
