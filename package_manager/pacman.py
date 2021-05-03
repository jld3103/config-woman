import functools
import gzip
import os.path
import subprocess

from package_manager.file import File
from package_manager.helpers import generate_modified_files_list, get_etc_files
from package_manager.package_manager import PackageManager


class Pacman(PackageManager):
    name = "pacman"

    def get_packages(self) -> [str]:
        packages = []
        for line in subprocess.check_output(['pacman', '-Q']).decode('utf-8').split('\n'):
            if len(line) > 0:
                packages.append(line.split(' ')[0])
        return packages

    def is_package_explicitly_installed(self, package) -> bool:
        return package in self._get_explicitly_installed_packages()

    @functools.lru_cache()
    def _get_explicitly_installed_packages(self) -> [str]:
        packages = []
        name = ""
        for line in subprocess.check_output(['pacman', '-Qi']).decode('utf-8').split('\n'):
            if line.startswith('Name'):
                name = line.split(': ')[1]
            if line.startswith('Install Reason'):
                if 'Explicitly installed' in line:
                    packages.append(name)
        return packages

    def install_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            os.system('pacman -S {package} --noconfirm'.format(package=' '.join(packages)))
        else:
            os.system('pacman -S {package}'.format(package=' '.join(packages)))

    def remove_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            os.system('pacman -Rns {package} --noconfirm'.format(package=' '.join(packages)))
        else:
            os.system('pacman -Rns {package}'.format(package=' '.join(packages)))

    def get_modified_files(self, excludes: [str]) -> [File]:
        etc_files = get_etc_files(excludes + ['/etc/pacman.d/gnupg'])
        registered_files = {}
        for root, _, files in os.walk('/var/lib/pacman/local'):
            for file_name in files:
                if file_name == 'mtree':
                    with gzip.open(os.path.join(root, file_name)) as mtree_file:
                        for line in mtree_file.read().decode('utf-8').split('\n'):
                            if line.startswith('./'):
                                path = line.split(' ')[0][1:]
                                is_dir = 'type=dir' in line
                                is_link = 'type=link' in line
                                if is_link:
                                    is_dir = os.path.isdir(os.path.realpath(path))
                                if path.startswith('/etc') and not is_dir:
                                    registered_files[path] = line.split(' ')[-1].split('=')[1]
        return generate_modified_files_list(etc_files, registered_files, 'sha256')
