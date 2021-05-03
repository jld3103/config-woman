import logging
import os
import sys

import click

from config import load_system_config, write_missing_system_config, Config, write_redundant_system_config
from defaults import default_config_directory
from helpers import get_installed_not_listed_packages, get_listed_not_installed_packages, get_system_package_manager, \
    get_base_distribution


def setup_logging(verbose: bool):
    level = logging.INFO
    if verbose:
        level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%m/%d/%Y %H:%M:%S',
        level=level
    )


verbose_option = click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Enables verbose mode'
)
config_directory_option = click.option(
    '-c',
    '--config-directory',
    'config_directory',
    default=default_config_directory,
    help='Config directory location',
)
no_confirm_option = click.option(
    '-y',
    '--no-confirm',
    'no_confirm',
    is_flag=True,
    help='Confirm package install/remove actions',
)
preset_argument = click.argument(
    'preset',
    envvar='PRESET',
    default='default'
)


@click.group()
def cli():
    pass


@click.group()
def system():
    setup_logging(False)
    if not os.geteuid() == 0:
        logging.fatal('You need to be root to run any system command')
        exit(1)


@click.command(name='save')
@verbose_option
@config_directory_option
@preset_argument
def system_save(verbose, config_directory, preset):
    setup_logging(verbose)

    package_manager = get_system_package_manager()
    config = load_system_config(config_directory, preset)

    installed_not_listed_packages: [str] = get_installed_not_listed_packages(config.packages, package_manager)
    logging.info('Detected {num} packages that are installed but not listed in the config.'.format(
        num=len(installed_not_listed_packages)))
    missing_config = Config(installed_not_listed_packages)
    write_missing_system_config(config_directory, preset, missing_config)

    listed_not_installed_packages: [str] = get_listed_not_installed_packages(config.packages, package_manager)
    logging.info('Detected {num} packages that are listed in the config but not installed.'.format(
        num=len(listed_not_installed_packages)))
    redundant_config = Config(listed_not_installed_packages)
    write_redundant_system_config(config_directory, preset, redundant_config)


@click.command(name='apply')
@verbose_option
@config_directory_option
@no_confirm_option
@preset_argument
def system_apply(verbose, config_directory, no_confirm, preset):
    setup_logging(verbose)

    package_manager = get_system_package_manager()
    config = load_system_config(config_directory, preset)

    listed_not_installed_packages: [str] = get_listed_not_installed_packages(config.packages, package_manager)
    if len(listed_not_installed_packages) == 0:
        logging.info('Detected no packages that are listed in the config but not installed.')
    else:
        logging.info(
            'Detected {num} packages that are listed in the config but not installed. Proceeding to install them.'.format(
                num=len(listed_not_installed_packages)))
        package_manager.install_packages(listed_not_installed_packages, no_confirm)

    installed_not_listed_packages: [str] = get_installed_not_listed_packages(config.packages, package_manager)
    if len(installed_not_listed_packages) == 0:
        logging.info('Detected no packages that are not listed in the config but installed.')
    else:
        logging.info(
            'Detected {num} packages that are not listed in the config but installed. Proceeding to remove them.'.format(
                num=len(installed_not_listed_packages)))
        package_manager.remove_packages(installed_not_listed_packages, no_confirm)


@click.group()
def user():
    pass


@click.command(name='save')
@verbose_option
@config_directory_option
def user_save(verbose):
    setup_logging(verbose)
    pass


@click.command(name='apply')
@verbose_option
@config_directory_option
def user_apply(verbose):
    setup_logging(verbose)
    pass


@click.command(name='info')
@verbose_option
def info(verbose):
    setup_logging(verbose)
    logging.info('Base distribution: %s', get_base_distribution())
    logging.info('Package manager: %s', get_system_package_manager().name)


system.add_command(system_save)
system.add_command(system_apply)
user.add_command(user_save)
user.add_command(user_apply)
cli.add_command(system)
cli.add_command(user)
cli.add_command(info)

if __name__ == '__main__':
    cli()
