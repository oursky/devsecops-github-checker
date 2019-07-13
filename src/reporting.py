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
        self.problem = []
        self.remedy = []


class Reporting():
    def __init__(self, verbose: bool = False):
        self._verbose = verbose
        self._results = []

    @property
    def total(self):
        return len(self._results)

    @property
    def warnings(self):
        return len([x for x in self._results if x.status == ScanResultStatus.WARN])

    @property
    def errors(self):
        return len([x for x in self._results if x.status == ScanResultStatus.ERROR])

    def authorized_as(self, username: str) -> None:
        print("Authorized as:", username)

    def working_on(self, current: int, total: int, slug: str) -> None:
        msg = "[{current:0=3d}/{total:0=3d}] [W:{warn:0=3d}|E:{err:0=3d}] {slug}".format(
            current=current,
            total=total,
            warn=self.warnings,
            err=self.errors,
            slug=slug,
        )
        print("\r{0: <78}\r".format(msg), end='')

    def report(self, result: ScanResult) -> None:
        self._results.append(result)

    def print(self):
        with open('result.txt', 'a') as logfile:
            msg = "\nSummary: {total} checked, {warn} warnings, {err} errors".format(
                total=self.total,
                warn=self.warnings,
                err=self.errors)
            print(msg)
            print(msg, file=logfile)
            for result in self._results:
                if result.status == ScanResultStatus.OK:
                    continue
                msg = "[{status}] {slug}: {file}\n    {problem}\n\n    Remedy: {remedy}".format(
                    status=result.status.value,
                    slug=result.reposlug,
                    file=result.filename,
                    problem="\n    ".join(result.problem),
                    remedy="\n            ".join(result.remedy))
                if self._verbose:
                    print(msg)
                print(msg, file=logfile)
