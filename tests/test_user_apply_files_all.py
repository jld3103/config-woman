import os
import subprocess

import yaml


def test_files():
    with open('system.yaml', 'w') as file:
        file.write(yaml.dump({'mode': 'user', 'files': {'.test': '1:2:611'}}))
    os.makedirs('system_files')
    with open('system_files/.test', 'w') as file:
        file.write('bla')
    subprocess.run(['python', 'main.py', 'user', 'apply'])
    with open('system_files/.test', 'r') as original_file:
        with open('/root/.test', 'r') as copied_file:
            assert copied_file.read() == original_file.read()
            stat_info = os.stat('/root/.test')
            assert stat_info.st_uid == 1
            assert stat_info.st_gid == 2
            assert stat_info.st_mode == 0o100611
