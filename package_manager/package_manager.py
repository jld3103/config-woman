import abc


class PackageManager(abc.ABC):

    @abc.abstractmethod
    def get_packages(self) -> [str]:
        pass

    @abc.abstractmethod
    def is_package_explicitly_installed(self, package: str) -> bool:
        pass

    @abc.abstractmethod
    def install_packages(self, packages: [str]):
        pass

    @abc.abstractmethod
    def remove_packages(self, packages: [str]):
        pass
