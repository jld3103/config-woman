import subprocess


def test_info():
    output = subprocess.check_output(['python', 'main.py', 'info']).decode('utf-8')
    assert 'Base distribution: arch' in output
    assert 'Package manager: pacman' in output
