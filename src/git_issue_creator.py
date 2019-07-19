from typing import Optional, List
from github import (
    Github,
    Repository,
    Label,
    Issue,
    GithubException,
    UnknownObjectException,
)
from results import ScanResultStatus, ScanResult, ScanResults


class GitIssueCreator():
    def __init__(self, github: Github, verbose: bool = False, create_issue: bool = False, create_pr: bool = False):
        self._verbose = verbose
        self._github = github
        self._should_create_issue = create_issue
        self._should_create_pr = create_pr

    def create_issues(self, results: ScanResults) -> None:
        for reposlug in results.results:
            if not results.have_problem(reposlug):
                continue
            try:
                repo = self._github.get_repo(reposlug)
            except UnknownObjectException:
                print("[E] Repository not found: ", reposlug)
                continue
            try:
                if self._should_create_issue:
                    self._emit_github_issue(reposlug, repo, results.results[reposlug])
                if self._should_create_pr:
                    self._emit_github_pr(reposlug, repo, results.results[reposlug])
            except Exception as e:
                print("[E] {} - {}".format(reposlug, str(e)))

    def _emit_github_issue(self, reposlug: str, repo: Repository, results: List[ScanResult]) -> None:
        title = "Missing entries in ignore file(s)"
        message = ""
        for result in results:
            if result.status == ScanResultStatus.OK:
                continue
            item = "Please add the following to {file}:\n```\n{fixes}\n```\n\n".format(
                file=result.filename,
                fixes="\n".join(result.missings))
            message = message + item
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

    def _emit_github_pr(self, reposlug: str, repo: Repository, results: List[ScanResult]) -> None:
        if len(results) == 0:
            return
        branch_name = "devsecops-ignore"
        if self._is_branch_exists(repo, branch_name):
            print("[I] There is already an PR for {}, skipping.".format(reposlug))
            return
        fromsha = results[0].commitsha
        ref = self._clone_branch(reposlug, repo, branch_name, fromsha)
        print("[I] Create branch: {}: {}".format(reposlug, ref))
        for result in results:
            self._create_fix(reposlug, repo, branch_name, result)
        self._create_pr(reposlug, repo, branch_name, "master")

    def _is_branch_exists(self, repo: Repository, branch: str) -> Optional[str]:
        try:
            b = repo.get_branch(branch)
            return b.commit.sha
        except GithubException:
            return None

    def _clone_branch(self, reposlug: str, repo: Repository, branch: str, fromsha: str) -> Optional[str]:
        try:
            ref = repo.create_git_ref(ref='refs/heads/' + branch, sha=fromsha)
            return ref.ref
        except GithubException:
            return None

    def _create_fix(self, reposlug: str, repo: Repository, branch: str, result: ScanResult) -> None:
        new_content = "{}\n{}\n".format(result.content, "\n".join(result.missings))
        repo.update_file(result.filename,
                         message="Autofix by devsecops",
                         content=new_content,
                         sha=result.filesha,
                         branch=branch)
        print("[I] Updated {}: {}".format(reposlug, result.filename))

    def _create_pr(self, reposlug: str, repo: Repository, branch: str, onto: str) -> None:
        repo.create_pull(title="Harden ignore files",
                         body="Autofix created by devsecops",
                         base=onto,
                         head=branch)
        print("[I] Created PR {}".format(reposlug))
