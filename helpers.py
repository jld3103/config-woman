import logging

import distro

from package_manager.apt import Apt
from package_manager.pacman import Pacman


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
    logging.debug('Detecting packages that are installed but not listed in the config')
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
    logging.debug('Detecting packages that are listed in the config but not installed')
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
