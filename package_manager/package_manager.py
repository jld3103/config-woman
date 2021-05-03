import abc

from package_manager.file import File


class PackageManager(abc.ABC):

    @abc.abstractmethod
    def get_packages(self) -> [str]:
        pass

    @abc.abstractmethod
    def is_package_explicitly_installed(self, package: str) -> bool:
        pass

    @abc.abstractmethod
    def install_packages(self, packages: [str], no_confirm: bool):
        pass

    @abc.abstractmethod
    def remove_packages(self, packages: [str], no_confirm: bool):
        pass

    @abc.abstractmethod
    def get_modified_files(self, excludes: [str]) -> [File]:
        pass
