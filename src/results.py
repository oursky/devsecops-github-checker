from enum import Enum


class ScanResultStatus(Enum):
    OK = "K"
    WARN = "W"
    ERROR = "E"


class ScanResult():
    def __init__(self,
                 status: ScanResultStatus,
                 reposlug: str,
                 filename: str):
        self.status = status
        self.reposlug = reposlug
        self.filename = filename
        self.missings = []


class ScanResults():
    def __init__(self):
        self.results = {}
        self.errors = 0
        self.warnings = 0

    @property
    def total(self):
        return len(self.results)

    def add(self, result: ScanResult) -> None:
        if result.status == ScanResultStatus.WARN:
            self.warnings = self.warnings + 1
        elif result.status == ScanResultStatus.ERROR:
            self.errors = self.errors + 1
        if result.reposlug not in self.results:
            self.results[result.reposlug] = []
        self.results[result.reposlug].append(result)

    def have_problem(self, reposlug) -> bool:
        if reposlug not in self.results:
            return False
        for result in self.results[reposlug]:
            if result.status != ScanResultStatus.OK:
                return True
        return False
