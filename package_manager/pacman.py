import subprocess
from package_manager.package_manager import PackageManager
from root import run_as_root


class Pacman(PackageManager):
    name = "pacman"

    def get_packages(self) -> [str]:
        packages = []
        for line in subprocess.check_output(['pacman', '-Q']).decode('utf-8').split('\n'):
            if len(line) > 0:
                packages.append(str(line.split(' ')[0]))
        return packages

    def is_package_explicitly_installed(self, package) -> bool:
        for line in subprocess.check_output(['pacman', '-Qi', package]).decode('utf-8').split('\n'):
            if line.startswith('Install Reason'):
                return 'Explicitly installed' in line
        return True

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
