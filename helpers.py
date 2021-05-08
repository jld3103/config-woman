import hashlib
import logging
import os
import re
import shutil

import distro

from config import Config
from package_manager.apt import Apt
from package_manager.pacman import Pacman
from utils import file_exists, file_info

used_exclude_files = []
used_content_filters = []


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
            if not check_is_excluded(file_path, exclude_files):
                all_files.append(file_path)
    return all_files


def get_modified_not_listed_files(config: Config, exclude_files: [str], registered_files: {}, hash_method: str) -> {}:
    modified_files = []
    new_files = get_etc_files(exclude_files).copy()

    for path in registered_files:
        if check_is_excluded(path, exclude_files):
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
            files[file] = file_info(file)

    return files


def get_listed_not_modified_files(config: Config, exclude_files: [str], registered_files: {}, hash_method: str) -> {}:
    not_modified_files = []

    for path in config.files:
        if check_is_excluded(path, exclude_files):
            not_modified_files.append(path)
            continue

        if not file_exists(path, follow_symlinks=False):
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


def save_files(config_directory: str, preset: str, files: {}, content_filters: [], relative_path: str):
    files_path = os.path.join(config_directory, f'{preset}_files')
    if os.path.exists(files_path):
        shutil.rmtree(files_path)
    os.mkdir(files_path)
    stat_info = os.stat(os.path.join(config_directory, '..'))
    for path in files:
        logging.debug(f'Saving {path}')
        local_path = os.path.join(files_path, path.strip('/'))
        local_dir = os.path.dirname(local_path)
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)
        absolute_path = os.path.join(relative_path, path)
        if file_exists(absolute_path, follow_symlinks=False):
            if os.path.islink(absolute_path):
                shutil.copy(absolute_path, local_path, follow_symlinks=False)
            else:
                content = read_filtered_content(absolute_path, content_filters, relative_path)
                if isinstance(content, str):
                    with open(local_path, 'w') as file:
                        file.write(content)
                else:
                    with open(local_path, 'wb') as file:
                        file.write(content)
                # So we are not annoying with the permissions for users
                os.chown(local_path, stat_info.st_uid, stat_info.st_gid)


def apply_files(config_directory: str, preset: str, files: {}, relative_path: str):
    files_path = os.path.join(config_directory, f'{preset}_files')
    if not os.path.exists(files_path):
        if len(files) > 0:
            logging.fatal(f'Could not find required {preset}_files directory')
            exit(1)
        return
    for path in files:
        logging.debug(f'Applying {path}')
        local_path = os.path.join(files_path, path.strip('/'))
        if file_exists(local_path, follow_symlinks=False):
            uid = int(files[path].split(':')[0])
            gid = int(files[path].split(':')[1])
            mode = int('100' + files[path].split(':')[2], 8)
            absolute_path = os.path.join(relative_path, path)
            if file_exists(absolute_path, follow_symlinks=False):
                os.remove(absolute_path)
            else:
                logging.debug(f'File {path} was not available on the system')
            if not file_exists(os.path.dirname(absolute_path), follow_symlinks=False):
                os.makedirs(os.path.dirname(absolute_path))
            shutil.copy(local_path, absolute_path, follow_symlinks=False)
            try:
                os.chown(absolute_path, uid, gid)
            except PermissionError:
                logging.warning(
                    f'Unable to chown {path}. This could be because it is a symlink or because you have set the wrong '
                    f'permissions on the file')
            try:
                os.chmod(absolute_path, mode)
            except PermissionError:
                logging.warning(
                    f'Unable to chmod {path}. This could be because it is a symlink or because you have set the wrong '
                    f'permissions on the file')

        else:
            logging.fatal(f'Could not find required {preset}_files{path} file')
            exit(1)


def get_available_not_listed_files(config: Config, exclude_files: [str]):
    not_listed_files = []
    home_dir = os.path.expanduser('~')
    all_files = []

    exclude_files_expanded = []
    for exclude_file in exclude_files:
        exclude_files_expanded.append(os.path.join(home_dir, exclude_file))

    for name in os.listdir(home_dir):
        if name.startswith('.'):
            if os.path.isfile(os.path.join(home_dir, name)):
                all_files.append(os.path.join(home_dir, name))
    for root, _, files in os.walk(os.path.join(home_dir, '.config')):
        for file in files:
            all_files.append(os.path.join(root, file))

    for path in all_files:
        if check_is_excluded(path, exclude_files_expanded):
            continue
        listed = False
        for file in config.files:
            if os.path.join(home_dir, file) == path:
                listed = True
                break
        if not listed:
            not_listed_files.append(path)

    files = {}
    for file in not_listed_files:
        if file not in config.files:
            files[os.path.relpath(file, home_dir)] = file_info(file)

    return files


def get_listed_not_available_files(config: Config, exclude_files: [str]):
    not_available_files = []
    home_dir = os.path.expanduser('~')

    for path in config.files:
        path = os.path.join(home_dir, path)
        if check_is_excluded(path, exclude_files):
            not_available_files.append(path)
            continue

        if not file_exists(path, follow_symlinks=False):
            not_available_files.append(os.path.relpath(path, home_dir))

    return not_available_files


def check_is_excluded(path: str, exclude_files: [str]) -> bool:
    for exclude_file in exclude_files:
        if _path_match_pattern(path, exclude_file):
            if exclude_file not in used_exclude_files:
                used_exclude_files.append(exclude_file)
            logging.debug(f'Excluding {path} because of exclude rule {exclude_file}')
            return True
    return False


def _path_match_pattern(path, pattern):
    return re.match(f'^{re.sub(r"/$", "/.*", pattern.replace("*", ".*"))}$', path)


def get_listed_not_used_exclude_files(config, relative_path):
    listed_not_used_exclude_files = []
    for exclude_file in config.exclude_files:
        if os.path.join(relative_path, exclude_file) not in used_exclude_files:
            listed_not_used_exclude_files.append(exclude_file)
    return listed_not_used_exclude_files


def read_filtered_content(path: str, content_filters: [], relative_path: str):
    filtered_content = []
    matching_content_filters = []
    for content_filter in content_filters:
        filter_path = list(content_filter.keys())[0]
        if _path_match_pattern(path, os.path.join(relative_path, filter_path)):
            matching_content_filters.append(content_filter)
    try:
        with open(path, 'r') as file:
            content = file.read()
            for line in content.split('\n'):
                do_filter = False
                for content_filter in matching_content_filters:
                    if re.match(f'^{content_filter[list(content_filter.keys())[0]]}$', line):
                        if path not in used_content_filters:
                            used_content_filters.append(content_filter)
                        do_filter = True
                        break
                if not do_filter:
                    filtered_content.append(line)
        return '\n'.join(filtered_content)
    except UnicodeDecodeError:
        with open(path, 'rb') as file:
            return file.read()


def get_listed_not_used_content_filters(config):
    listed_not_used_content_filters = []
    for content_filter1 in config.content_filters:
        used = False
        path1 = list(content_filter1.keys())[0]
        for content_filter2 in used_content_filters:
            path2 = list(content_filter2.keys())[0]
            if path1 == path2 and content_filter1[path1] == content_filter2[path2]:
                used = True
        if not used:
            listed_not_used_content_filters.append(content_filter1)
    return listed_not_used_content_filters
