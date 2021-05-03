import hashlib
import logging
import os

from package_manager.file import File


def get_etc_files(excludes: [str]):
    # Some dirs to exclude by default
    excludes += ['/etc/ca-certificates', '/etc/ssl']
    all_files = []
    for root, sub_dirs, files in os.walk('/etc'):
        for file in files:
            file_path = os.path.join(root, file)
            do_exclude = False
            for exclude in excludes:
                if file_path.startswith(exclude):
                    do_exclude = True
                    logging.debug(f'Excluding {file_path} because of exclude rule {exclude}')
                    break
            if not do_exclude:
                all_files.append(file_path)
    return all_files


def generate_modified_files_list(etc_files: [str], registered_files: {}, hash_method: str) -> [File]:
    modified_files = []
    new_files = etc_files.copy()

    for path in registered_files:
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
