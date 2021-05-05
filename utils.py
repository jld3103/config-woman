import os


def file_exists(path: str, follow_symlinks: bool = True) -> bool:
    if follow_symlinks:
        return os.path.exists(path)
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False
