from tests.common_system_save_missing_packages import common_missing_packages


def test_missing():
    common_missing_packages('python3', 'gnome-backgrounds')
