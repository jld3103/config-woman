import subprocess
from package_manager.package_manager import PackageManager


class Apt(PackageManager):
    name = "apt"

    def get_packages(self) -> [str]:
        packages = []
        for line in subprocess.check_output(['apt', 'list']).decode('utf-8').split('\n'):
            if len(line) > 0:
                packages.append(str(line.split(' ')[0].split('/')[0]))
        return packages

    def is_package_explicitly_installed(self, package) -> bool:
        pass

    def install_packages(self, packages: [str], no_confirm: bool):
        pass

    def remove_packages(self, packages: [str], no_confirm: bool):
        pass
