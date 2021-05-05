import hashlib
import logging
import os

import distro

from config import Config
from package_manager.apt import Apt
from package_manager.pacman import Pacman

used_exclude_files = []


def get_base_distribution():
    base_distribution = distro.like()
    if base_distribution == '':
        base_distribution = distro.id()
    if base_distribution == '':
        logging.fatal(
            'Unable to detect your distribution. Please file a bug with the following information included:\n%s',
            distro.linux_distribution(full_distribution_name=False))
        exit(1)
    return base_distribution


def get_system_package_manager():
    base_distribution = get_base_distribution()
    logging.debug('Detected \'%s\' as base distribution', base_distribution)
    distribution_package_manager_map = {
        'arch': Pacman(),
        'debian': Apt(),
    }
    package_manager = distribution_package_manager_map.get(base_distribution)
    logging.debug('Using \'%s\' as package manager', package_manager.name)
    return package_manager


def get_installed_not_listed_packages(listed_packages: [str], package_manager) -> [str]:
    installed_not_listed_packages: [str] = []
    installed_packages = package_manager.get_packages()
    for installed_package in installed_packages:
        found = False
        for listed_package in listed_packages:
            if installed_package == listed_package:
                found = True
        if not found and package_manager.is_package_explicitly_installed(installed_package):
            logging.debug(f'\'{installed_package}\' installed but not listed')
            installed_not_listed_packages.append(installed_package)
    return installed_not_listed_packages


def get_listed_not_installed_packages(listed_packages: [str], package_manager) -> [str]:
    listed_not_installed_packages: [str] = []
    installed_packages = package_manager.get_packages()
    for listed_package in listed_packages:
        found = False
        for installed_package in installed_packages:
            if listed_package == installed_package:
                found = True
        if not found:
            logging.debug(f'\'{listed_package}\' listed but not installed')
            listed_not_installed_packages.append(listed_package)
    return listed_not_installed_packages


def get_etc_files(exclude_files: [str]):
    all_files = []
    for root, sub_dirs, files in os.walk('/etc'):
        for file in files:
            file_path = os.path.join(root, file)
            do_exclude = False
            for exclude_file in exclude_files:
                if file_path.startswith(exclude_file):
                    used_exclude_files.append(exclude_file)
                    do_exclude = True
                    logging.debug(f'Excluding {file_path} because of exclude rule {exclude_file}')
                    break
            if not do_exclude:
                all_files.append(file_path)
    return all_files


def get_modified_not_listed_files(config: Config, exclude_files: [str], registered_files: {}, hash_method: str) -> {}:
    modified_files = []
    new_files = get_etc_files(exclude_files).copy()

    for path in registered_files:
        skip = False
        for exclude_file in exclude_files:
            if path.startswith(exclude_file):
                used_exclude_files.append(exclude_file)
                skip = True
                break
        if skip:
            continue
        if path in new_files:
            new_files.remove(path)

        should_hash_sum = registered_files[path]

        # We got an empty hash that means the file is a symlink
        if should_hash_sum == '':
            continue

        if not verify_hash(path, should_hash_sum, hash_method):
            modified_files.append(path)

    for new_file in new_files:
        modified_files.append(new_file)

    files = {}
    for file in modified_files:
        if file not in config.files:
            try:
                stat_info = os.stat(file, follow_symlinks=False)
                files[file] = f'{stat_info.st_uid}:{stat_info.st_gid}:{oct(stat_info.st_mode)[-3:]}'
            except FileNotFoundError:
                logging.fatal(f'Could not find: {file}. It is very likely a dead symlink')
                exit(1)

    return files


def get_listed_not_modified_files(config: Config, exclude_files: [str], registered_files: {}, hash_method: str) -> {}:
    not_modified_files = []

    for path in config.files:
        remove = False
        for exclude_file in exclude_files:
            if path.startswith(exclude_file):
                used_exclude_files.append(exclude_file)
                remove = True
                break
        if remove:
            not_modified_files.append(path)
            continue

        if not os.path.exists(path):
            not_modified_files.append(path)

        if path in registered_files:
            should_hash_sum = registered_files[path]

            # We got an empty hash that means the file is a symlink
            if should_hash_sum == '':
                continue

            if verify_hash(path, should_hash_sum, hash_method):
                not_modified_files.append(path)

    return not_modified_files


def verify_hash(path, should_hash_sum, hash_method):
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
    return is_hash_sum == should_hash_sum
