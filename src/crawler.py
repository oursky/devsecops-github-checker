from typing import Optional
from github import (
    Github,
    GithubException,
    RateLimitExceededException,
    NamedUser,
    Organization,
    Repository,
    ContentFile,
)
from reporting import Reporting
from file_scanner_gitignore import GitIgnoreFileScanner
from file_scanner_dockerignore import DockerIgnoreFileScanner
from file_scanner_gcloudignore import GCloudIgnoreFileScanner


class GithubCrawler():
    def __init__(self, access_token: str, organization: Optional[str], reporting: Reporting):
        self._reporting = reporting
        self._github = Github(access_token)
        self._organization = organization
        self._scanners = [
            GitIgnoreFileScanner(),
            DockerIgnoreFileScanner(),
            GCloudIgnoreFileScanner(),
        ]

    def scan(self) -> None:
        try:
            user = self._github.get_user()
            self._reporting.authorized_as(user.login)
            for org in sorted(user.get_orgs(), key=lambda x: x.login):
                self._scan_organization(user, org)
        except RateLimitExceededException as e:
            print(e)

    def _scan_organization(self, user: NamedUser, org: Organization) -> None:
        if self._organization and org.login != self._organization:
            return
        repos = sorted(org.get_repos(), key=lambda x: x.name)
        for index, repo in enumerate(repos):
            self._reporting.working_on(index + 1, len(repos), "{}/{}".format(org.login, repo.name))
            self._scan_repository(user, org, repo)

    def _scan_repository(self, user: NamedUser, org: Organization, repo: Repository) -> None:
        try:
            branch = repo.get_branch(branch="master")
            tree = repo.get_git_tree(branch.commit.sha, recursive=True).tree
        except GithubException:
            # Skip if no master branch
            return
        for element in tree:
            self._scan_file(user, org, repo, element.path, branch.commit.sha)

    def _scan_file(self, user: NamedUser, org: Organization, repo: Repository, filename: str, sha: str) -> None:
        file: Optional(ContentFile) = None
        for scanner in self._scanners:
            if scanner.want(filename):
                if not file:
                    file = repo.get_contents(filename, ref=sha)
                reposlug = "{}/{}".format(org.login, repo.name)
                result = scanner.check(reposlug, file.path, file.decoded_content)
                self._reporting.report(result)
