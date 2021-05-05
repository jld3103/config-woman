import functools
import gzip
import os.path
import subprocess

from package_manager.package_manager import PackageManager
from utils import file_exists


class Pacman(PackageManager):
    name = "pacman"
    exclude_files = ['/etc/pacman.d/gnupg']
    hash_method = 'sha256'
    updates_fetched = False

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
        self.fetch_updates()
        if no_confirm:
            os.system(f'pacman -S {" ".join(packages)} --noconfirm')
        else:
            os.system(f'pacman -S {" ".join(packages)}')

    def remove_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            os.system(f'pacman -Rns {" ".join(packages)} --noconfirm')
        else:
            os.system(f'pacman -Rns {" ".join(packages)}')

    def fetch_updates(self):
        if not self.updates_fetched:
            os.system('pacman -Sy')
            self.updates_fetched = True

    def get_registered_files(self) -> {}:
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
                                if path.startswith('/etc') and not is_dir and file_exists(path, follow_symlinks=False):
                                    if is_link:
                                        registered_files[path] = ''
                                    else:
                                        registered_files[path] = line.split(' ')[-1].split('=')[1]
        return registered_files
