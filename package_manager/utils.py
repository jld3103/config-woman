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
