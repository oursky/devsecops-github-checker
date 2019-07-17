import abc
from typing import List
from reporting import ScanResult


class FileScanner(abc.ABC):
    @abc.abstractmethod
    def want(self, filename: str) -> bool:
        pass

    @abc.abstractmethod
    def check(self, reposlug: str, filename: str, content: str, filelist: List[str]) -> ScanResult:
        pass
