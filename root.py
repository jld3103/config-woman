import logging
import os
import shutil

from defaults import default_config_directory


def run_as_root(cmd):
    logging.info('Running as root: {cmd}'.format(cmd=cmd))
    if os.geteuid() == 0:
        return os.system(cmd)
    if shutil.which('sudo'):
        return os.system('sudo {cmd}'.format(cmd=cmd))
    if shutil.which('doas'):
        return os.system('doas {cmd}'.format(cmd=cmd))
    if shutil.which('su'):
        return os.system('su -c {cmd}'.format(cmd=cmd))
    logging.fatal(
        'Unable to detect a way to run commands as root. Please file a bug and describe the way you normally use to '
        'run commands as root.\n'
        'For example \'I use `sudo`, please add it\'.\n'
        'For the time being please run this tool with root directly and point to your config directory using the '
        '\'--config-directory={path}\' parameter.'.format(path=default_config_directory)
    )
    exit(1)
