import logging
import os


def file_exists(path: str, follow_symlinks: bool = True) -> bool:
    if follow_symlinks:
        return os.path.exists(path)
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False


def file_info(path: str):
    try:
        stat_info = os.stat(path, follow_symlinks=False)
        return f'{stat_info.st_uid}:{stat_info.st_gid}:{oct(stat_info.st_mode)[-3:]}'
    except FileNotFoundError:
        logging.fatal(f'Could not find: {path}. It is very likely a dead symlink')
        exit(1)
