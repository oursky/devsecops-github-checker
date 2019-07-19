from typing import Optional, List
from github import (
    Github,
    GithubException,
    RateLimitExceededException,
    NamedUser,
    Organization,
    Repository,
    ContentFile,
)
from results import ScanResults
from file_scanner_gitignore import GitIgnoreFileScanner
from file_scanner_dockerignore import DockerIgnoreFileScanner
from file_scanner_gcloudignore import GCloudIgnoreFileScanner


class GithubCrawler():
    def __init__(self, github: Github, organization: Optional[str]):
        self._github = github
        self._organization = organization
        self._scanners = [
            GitIgnoreFileScanner(),
            DockerIgnoreFileScanner(),
            GCloudIgnoreFileScanner(),
        ]

    def scan(self, results: ScanResults) -> None:
        try:
            user = self._github.get_user()
            print("Authorized as:", user.login)
            for org in sorted(user.get_orgs(), key=lambda x: x.login):
                self._scan_organization(results, user, org)
        except RateLimitExceededException as e:
            print(e)

    def _scan_organization(self, results: ScanResults, user: NamedUser, org: Organization) -> None:
        if self._organization and org.login != self._organization:
            return
        repos = sorted(org.get_repos(), key=lambda x: x.name)
        for index, repo in enumerate(repos):
            msg = "[{current:03d}/{total:03d}] [W:{warn:03d}|E:{err:03d}] {slug}".format(
                current=index + 1,
                total=len(repos),
                warn=results.warnings,
                err=results.errors,
                slug="{}/{}".format(org.login, repo.name)
            )
            print("\r{0: <78}\r".format(msg), end='')
            if repo.archived or repo.fork:
                continue
            self._scan_repository(results, user, org, repo)

    def _scan_repository(self, results: ScanResults, user: NamedUser, org: Organization, repo: Repository) -> None:
        try:
            branch = repo.get_branch(branch="master")
            tree = repo.get_git_tree(branch.commit.sha, recursive=True).tree
        except GithubException as e:
            print("[W] {}/{} - {}".format(org.login, repo.name, str(e)))
            # Skip if no master branch
            return
        filelist = [x.path for x in tree]
        for element in tree:
            self._scan_file(results, user, org, repo, branch.commit.sha, element.path, filelist)

    def _scan_file(self,
                   results: ScanResults,
                   user: NamedUser,
                   org: Organization,
                   repo: Repository,
                   commitsha: str,
                   filename: str,
                   filelist: List[str]) -> None:
        file: Optional(ContentFile) = None
        content: str = None
        for scanner in self._scanners:
            if scanner.want(filename):
                if not file:
                    file = repo.get_contents(filename, ref=commitsha)
                    content = file.decoded_content.decode("utf-8")
                reposlug = "{}/{}".format(org.login, repo.name)
                result = scanner.check(reposlug, commitsha, file.sha, file.path, content, filelist)
                results.add(result)
