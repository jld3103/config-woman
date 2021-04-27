import logging


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
            logging.debug('\'{package}\' installed but not listed'.format(package=installed_package))
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
            logging.debug('\'{package}\' listed but not installed'.format(package=listed_package))
            listed_not_installed_packages.append(listed_package)
    return listed_not_installed_packages
