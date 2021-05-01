import subprocess
from package_manager.package_manager import PackageManager
from root import run_as_root
import functools


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
            run_as_root('apt-get install {package} -y'.format(package=' '.join(packages)))
        else:
            run_as_root('apt-get install {package}'.format(package=' '.join(packages)))

    def remove_packages(self, packages: [str], no_confirm: bool):
        if no_confirm:
            run_as_root('apt-get purge {package} -y'.format(package=' '.join(packages)))
        else:
            run_as_root('apt-get purge {package}'.format(package=' '.join(packages)))
