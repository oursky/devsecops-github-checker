import abc


class FileScanner(abc.ABC):
    @abc.abstractmethod
    def want(self, filename: str) -> bool:
        pass

    @abc.abstractmethod
    def check(self, filename: str, content: str) -> bool:
        pass
