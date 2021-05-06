import os

import appdirs

default_config_directory = ""

if os.getenv('CONFIG_DIR') is not None:
    default_config_directory = os.path.join(os.getenv('CONFIG_DIR'))
else:
    default_config_directory = os.path.join(appdirs.user_config_dir(), 'config-woman')

default_system_exclude_files = [
    '/etc/ca-certificates',
    '/etc/ssl',
    '/etc/.updated'
]
default_user_exclude_files = [
    '.bash_history',
    '.python_history',
    '.ICEauthority',
    '.Xauthority',
    '.xsession-errors',
    '.pulse-cookie',
    '.config/config-woman'
]
