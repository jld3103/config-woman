import subprocess


def test_info():
    output = subprocess.check_output(['python', 'main.py', 'info']).decode('utf-8')
    assert 'Base distribution: debian' in output
    assert 'Package manager: apt' in output
