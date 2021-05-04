import hashlib
import logging
import os

from package_manager.file import File


def get_etc_files(exclude_files: [str]):
    all_files = []
    for root, sub_dirs, files in os.walk('/etc'):
        for file in files:
            file_path = os.path.join(root, file)
            do_exclude = False
            for exclude_file in exclude_files:
                if file_path.startswith(exclude_file):
                    do_exclude = True
                    logging.debug(f'Excluding {file_path} because of exclude rule {exclude_file}')
                    break
            if not do_exclude:
                all_files.append(file_path)
    return all_files


def generate_modified_files_list(exclude_files: [str], registered_files: {}, hash_method: str) -> [File]:
    modified_files = []
    new_files = get_etc_files(exclude_files).copy()

    for path in registered_files:
        skip = False
        for exclude_file in exclude_files:
            if path.startswith(exclude_file):
                skip = True
                break
        if skip:
            continue
        if path in new_files:
            new_files.remove(path)

        should_hash_sum = registered_files[path]

        file_hash = None
        if hash_method == 'sha256':
            file_hash = hashlib.sha256()
        elif hash_method == 'md5':
            file_hash = hashlib.md5()
        else:
            logging.fatal(f'Unsupported hash method: {hash_method}')
            exit(1)
        with open(path, 'rb') as file:
            fb = file.read(65536)
            while len(fb) > 0:
                file_hash.update(fb)
                fb = file.read(65536)
        is_hash_sum = file_hash.hexdigest()
        if is_hash_sum != should_hash_sum:
            modified_files.append(File(path, False, True))

    for new_file in new_files:
        modified_files.append(File(new_file, True, False))

    return modified_files
