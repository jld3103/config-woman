import functools
import subprocess
from package_manager.package_manager import PackageManager
from root import run_as_root


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
            run_as_root('pacman -S {package} --noconfirm'.format(package=' '.join(packages)))
        else:
            run_as_root('pacman -S {package}'.format(package=' '.join(packages)))

    def remove_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            run_as_root('pacman -Rns {package} --noconfirm'.format(package=' '.join(packages)))
        else:
            run_as_root('pacman -Rns {package}'.format(package=' '.join(packages)))
