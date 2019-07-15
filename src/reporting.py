from typing import List
from enum import Enum
from github import (
    Github,
)


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
    def __init__(self, github: Github, verbose: bool = False):
        self._verbose = verbose
        self._github = github
        self._results = {}
        self._warnings = 0
        self._errors = 0

    def authorized_as(self, username: str) -> None:
        print("Authorized as:", username)

    def working_on(self, current: int, total: int, slug: str) -> None:
        msg = "[{current:03d}/{total:03d}] [W:{warn:03d}|E:{err:03d}] {slug}".format(
            current=current,
            total=total,
            warn=self._warnings,
            err=self._errors,
            slug=slug,
        )
        print("\r{0: <78}\r".format(msg), end='')

    def report(self, result: ScanResult) -> None:
        if result.status == ScanResultStatus.WARN:
            self._warnings = self._warnings + 1
        elif result.status == ScanResultStatus.ERROR:
            self._errors = self._errors + 1
        if result.reposlug not in self._results:
            self._results[result.reposlug] = []
        self._results[result.reposlug].append(result)

    def print(self):
        with open('result.txt', 'a') as logfile:
            msg = "\nSummary: {total} repo checked, {warn} warnings, {err} errors".format(
                total=len(self._results),
                warn=self._warnings,
                err=self._errors)
            print(msg)
            print(msg, file=logfile)
            for reposlug in self._results:
                issue = self._build_issue(self._results[reposlug])
                if not issue:
                    continue
                if self._verbose:
                    print(issue)
                print(issue, file=logfile)

    def _build_issue(self, results: List[ScanResult]) -> str:
        issue = ""
        for result in results:
            if result.status == ScanResultStatus.OK:
                continue
            msg = "[{status}] {slug}: {file}\n    {problem}\n\n    Remedy: {remedy}\n".format(
                status=result.status.value,
                slug=result.reposlug,
                file=result.filename,
                problem="\n    ".join(result.problem),
                remedy="\n            ".join(result.remedy))
            issue = issue + msg
        return issue
