import functools
import os
import subprocess

from package_manager.file import File
from package_manager.helpers import get_etc_files, generate_modified_files_list
from package_manager.package_manager import PackageManager


class Apt(PackageManager):
    name = "apt"

    def get_packages(self) -> [str]:
        packages = []
        for line in subprocess.check_output(['apt', 'list', '--installed']).decode('utf-8').split('\n'):
            if len(line) > 0:
                packages.append(line.split(' ')[0].split('/')[0])
        return packages

    def is_package_explicitly_installed(self, package) -> bool:
        return package in self._get_explicitly_installed_packages()

    @functools.lru_cache()
    def _get_explicitly_installed_packages(self) -> [str]:
        packages = []
        for line in subprocess.check_output(['apt-mark', 'showmanual']).decode('utf-8').split('\n'):
            if len(line) > 0:
                packages.append(line)
        return packages

    def install_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            os.system(f'apt-get install {" ".join(packages)} -y')
        else:
            os.system(f'apt-get install {" ".join(packages)}')

    def remove_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            os.system(f'apt-get purge {" ".join(packages)} -y')
        else:
            os.system(f'apt-get purge {" ".join(packages)}')

    def get_modified_files(self, excludes: [str]) -> [File]:
        etc_files = get_etc_files(excludes + [])
        registered_files = {}
        for root, _, files in os.walk('/var/lib/dpkg/info'):
            for file_name in files:
                if file_name.endswith('md5sums'):
                    with open(os.path.join(root, file_name)) as md5sums_file:
                        for line in md5sums_file.read().split('\n'):
                            if len(line) > 0:
                                path = '/' + line.split('  ')[1]
                                if os.path.exists(path):
                                    registered_files[path] = line.split('  ')[0]
        return generate_modified_files_list(etc_files, registered_files, 'md5')
