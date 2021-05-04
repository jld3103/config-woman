import abc


class PackageManager(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def exclude_files(self) -> [str]:
        pass

    @property
    @abc.abstractmethod
    def hash_method(self) -> str:
        pass

    @abc.abstractmethod
    def updates_fetched(self) -> bool:
        pass

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
    def fetch_updates(self):
        pass

    @abc.abstractmethod
    def get_registered_files(self) -> {}:
        pass
