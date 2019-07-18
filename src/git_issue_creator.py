from typing import List
from github import (
    Github,
    Repository,
    Label,
    Issue,
    UnknownObjectException,
)
from results import ScanResultStatus, ScanResult, ScanResults


class GitIssueCreator():
    def __init__(self, github: Github, verbose: bool = False):
        self._verbose = verbose
        self._github = github

    def create_issues(self, results: ScanResults) -> None:
        for reposlug in results.results:
            if not results.have_problem(reposlug):
                continue
            try:
                self._emit_github_issue(reposlug, results.results[reposlug])
            except Exception as e:
                print("[E] {} - {}".format(reposlug, str(e)))

    def _emit_github_issue(self, reposlug: str, results: List[ScanResult]) -> None:
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
