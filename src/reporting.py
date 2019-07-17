from typing import List, TextIO
from enum import Enum
from github import (
    Github,
    Repository,
    Label,
    Issue,
    UnknownObjectException,
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
        self.missings = []
        self.remedy = []


class Reporting():
    def __init__(self, github: Github, verbose: bool = False, create_git_issue: bool = False):
        self._verbose = verbose
        self._create_git_issue = create_git_issue
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
                if not self._have_problem(self._results[reposlug]):
                    continue
                self._emit_log(reposlug, self._results[reposlug], logfile)
                try:
                    self._emit_github_issue(reposlug, self._results[reposlug])
                except Exception as e:
                    print("[E] {} - {}".format(reposlug, str(e)))

    def _have_problem(self, results: List[ScanResult]) -> bool:
        for result in results:
            if result.status != ScanResultStatus.OK:
                return True
        return False

    def _emit_log(self, reposlug: str, results: List[ScanResult], logfile: TextIO) -> None:
        message = ""
        for result in results:
            if result.status == ScanResultStatus.OK:
                continue
            item = "[{status}] {slug}: {file}\n    {problem}\n\n    Remedy: {remedy}\n".format(
                status=result.status.value,
                slug=result.reposlug,
                file=result.filename,
                problem="\n    ".join(result.problem),
                remedy="\n            ".join(result.remedy))
            message = message + item
        if self._verbose:
            print(message)
        print(message, file=logfile)

    def _emit_github_issue(self, reposlug: str, results: List[ScanResult]) -> None:
        if not self._create_git_issue:
            return
        title = "Missing entries in ignore file(s)"
        message = ""
        for result in results:
            if result.status == ScanResultStatus.OK:
                continue
            item = "Please add the following to {file}:\n```\n{fixes}\n```\n\n".format(
                file=result.filename,
                fixes="\n".join(result.missings))
            message = message + item
        # get repo
        try:
            repo = self._github.get_repo(reposlug)
        except UnknownObjectException:
            print("[E] Repository not found: ", reposlug)
            return
        label = self._create_label_if_needed(reposlug, repo, "devsecops", "Issues related to security", "3c4e90")
        self._create_or_update_issue(reposlug, repo, label, title, message)

    def _create_label_if_needed(self, reposlug: str, repo: Repository, name: str, desc: str, color: str) -> Label:
        try:
            label = repo.get_label("devsecops")
        except UnknownObjectException:
            if self._verbose:
                print("[I] Creating label {}:{}".format(reposlug, name))
            label = repo.create_label(name, color, desc)
        return label

    def _find_issue(self, repo: Repository, label: Label, title: str) -> Issue:
        issues = repo.get_issues(labels=[label])
        for issue in issues:
            if issue.title == title and issue.state == "open":
                return issue
        return None

    def _create_or_update_issue(self, reposlug: str, repo: Repository, label: Label, title: str, body: str) -> None:
        issue = self._find_issue(repo, label, title)
        if issue:
            issue.edit(body=body)
            if self._verbose:
                print("[I] Updated issue https://github.com/{}/issues/{}".format(reposlug, issue.number))
        else:
            issue = repo.create_issue(title, body, labels=[label])
            if self._verbose:
                print("[I] Created issue https://github.com/{}/issues/{}".format(reposlug, issue.number))
