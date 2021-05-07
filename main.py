import logging
import os
import sys

import click

from config import load_config, write_missing_config, Config, write_redundant_config
from defaults import default_config_directory, default_system_exclude_files, default_user_exclude_files
from helpers import get_installed_not_listed_packages, get_listed_not_installed_packages, get_system_package_manager, \
    get_base_distribution, get_modified_not_listed_files, get_listed_not_modified_files, save_files, apply_files, \
    get_available_not_listed_files, get_listed_not_available_files, \
    get_listed_not_used_exclude_files, get_listed_not_used_content_filters


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


def preset_argument(mode):
    return click.argument(
        'preset',
        envvar='PRESET',
        default=f'default_{mode}'
    )


@click.group()
def cli():
    pass


@click.group()
def system():
    if not os.geteuid() == 0:
        logging.fatal('You need to be root to run any system command')
        exit(1)


@click.command(name='save')
@verbose_option
@config_directory_option
@preset_argument('system')
def system_save(verbose, config_directory, preset):
    setup_logging(verbose)

    package_manager = get_system_package_manager()
    config = load_config('system', config_directory, preset)

    installed_not_listed_packages: [str] = get_installed_not_listed_packages(config.packages, package_manager)
    logging.info(
        f'Detected {len(installed_not_listed_packages)} packages that are installed but not listed in the config.')

    listed_not_installed_packages: [str] = get_listed_not_installed_packages(config.packages, package_manager)
    logging.info(
        f'Detected {len(listed_not_installed_packages)} packages that are listed in the config but not installed.')

    modified_not_listed_files: {} = get_modified_not_listed_files(
        config,
        default_system_exclude_files + config.exclude_files + package_manager.exclude_files,
        package_manager.get_registered_files(),
        package_manager.hash_method,
    )
    logging.info(
        f'Detected {len(modified_not_listed_files)} files that are modified but not listed in the config.')

    listed_not_modified_files: {} = get_listed_not_modified_files(
        config,
        default_system_exclude_files + config.exclude_files + package_manager.exclude_files,
        package_manager.get_registered_files(),
        package_manager.hash_method,
    )
    logging.info(f'Detected {len(listed_not_modified_files)} files that are listed in the config but not modified.')

    listed_not_used_exclude_files = get_listed_not_used_exclude_files(config, '/')
    logging.info(
        f'Detected {len(listed_not_used_exclude_files)} exclude rules that are listed in the config but not used.')

    listed_not_used_content_filters = get_listed_not_used_content_filters(config)
    logging.info(
        f'Detected {len(listed_not_used_content_filters)} config filters that are listed in the config but not used.')

    logging.info(f'Saving {len(config.files)} system configuration files')
    save_files(config_directory, preset, config.files, config.content_filters, '/')

    write_missing_config(
        config_directory,
        preset,
        Config(
            'system',
            installed_not_listed_packages,
            modified_not_listed_files,
            [],
            [],
        ),
    )
    write_redundant_config(
        config_directory,
        preset,
        Config(
            'system',
            listed_not_installed_packages,
            listed_not_modified_files,
            listed_not_used_exclude_files,
            listed_not_used_content_filters,
        ),
    )


@click.command(name='apply')
@verbose_option
@config_directory_option
@no_confirm_option
@preset_argument('system')
def system_apply(verbose, config_directory, no_confirm, preset):
    setup_logging(verbose)

    package_manager = get_system_package_manager()
    config = load_config('system', config_directory, preset)

    listed_not_installed_packages: [str] = get_listed_not_installed_packages(config.packages, package_manager)
    if len(listed_not_installed_packages) == 0:
        logging.info('Detected no packages that are listed in the config but not installed.')
    else:
        logging.info(
            f'Detected {len(listed_not_installed_packages)} packages that are listed in the config but not installed. '
            f'Proceeding to install them.')
        package_manager.install_packages(listed_not_installed_packages, no_confirm)

    installed_not_listed_packages: [str] = get_installed_not_listed_packages(config.packages, package_manager)
    if len(installed_not_listed_packages) == 0:
        logging.info('Detected no packages that are not listed in the config but installed.')
    else:
        logging.info(
            f'Detected {len(installed_not_listed_packages)} packages that are not listed in the config but installed. '
            f'Proceeding to remove them.')
        package_manager.remove_packages(installed_not_listed_packages, no_confirm)

    logging.info(f'Applying {len(config.files)} system configuration files')
    apply_files(config_directory, preset, config.files, '/')


@click.group()
def user():
    pass


@click.command(name='save')
@verbose_option
@config_directory_option
@preset_argument('user')
def user_save(verbose, config_directory, preset):
    setup_logging(verbose)

    config = load_config('user', config_directory, preset)

    available_not_listed_files: {} = get_available_not_listed_files(
        config,
        default_user_exclude_files + config.exclude_files,
    )
    logging.info(
        f'Detected {len(available_not_listed_files)} files that are available but not listed in the config.')

    listed_not_available_files: {} = get_listed_not_available_files(
        config,
        default_user_exclude_files + config.exclude_files,
    )
    logging.info(f'Detected {len(listed_not_available_files)} files that are listed in the config but not available.')

    listed_not_used_exclude_files = get_listed_not_used_exclude_files(config, os.path.expanduser('~'))
    logging.info(
        f'Detected {len(listed_not_used_exclude_files)} exclude rules that are listed in the config but not used.')

    logging.info(f'Saving {len(config.files)} user configuration files')
    save_files(config_directory, preset, config.files, config.content_filters, os.path.expanduser('~'))

    listed_not_used_content_filters = get_listed_not_used_content_filters(config)
    logging.info(
        f'Detected {len(listed_not_used_content_filters)} content filters that are listed in the config but not used.')

    write_missing_config(
        config_directory,
        preset,
        Config(
            'user',
            [],
            available_not_listed_files,
            [],
            [],
        ),
    )
    write_redundant_config(
        config_directory,
        preset,
        Config(
            'user',
            [],
            listed_not_available_files,
            listed_not_used_exclude_files,
            listed_not_used_content_filters,
        ),
    )
    pass


@click.command(name='apply')
@verbose_option
@config_directory_option
@preset_argument('user')
def user_apply(verbose, config_directory, preset):
    setup_logging(verbose)

    config = load_config('user', config_directory, preset)

    logging.info(f'Applying {len(config.files)} user configuration files')
    apply_files(config_directory, preset, config.files, os.path.expanduser('~'))
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
