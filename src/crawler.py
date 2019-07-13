from typing import Optional
from github import (
    Github,
    GithubException,
    NamedUser,
    Organization,
    Repository,
    ContentFile,
)
from file_scanner_gitignore import GitIgnoreFileScanner
from file_scanner_dockerignore import DockerIgnoreFileScanner


class GithubCrawler:
    def __init__(self, access_token: str, organization: Optional[str] = None, verbose: bool = False):
        self._verbose = verbose
        self._github = Github(access_token)
        self._organization = organization
        self._scanners = [
            GitIgnoreFileScanner(),
            DockerIgnoreFileScanner(),
        ]

    def scan(self) -> None:
        user = self._github.get_user()
        for org in user.get_orgs():
            self._scan_organization(user, org)

    def _scan_organization(self, user: NamedUser, org: Organization) -> None:
        if self._organization and org.login != self._organization:
            return
        for repo in org.get_repos():
            self._scan_repository(user, org, repo)

    def _scan_repository(self, user: NamedUser, org: Organization, repo: Repository) -> None:
        try:
            branch = repo.get_branch(branch="master")
            tree = repo.get_git_tree(branch.commit.sha, recursive=True).tree
        except GithubException:
            # Skip if no master branch
            return
        if self._verbose:
            print("[I] Scanning {}/{}...".format(org.login, repo.name))
        for file in tree:
            self._scan_file(user, org, repo, file.path)

    def _scan_file(self, user: NamedUser, org: Organization, repo: Repository, filename: str) -> None:
        file: Optional(ContentFile) = None
        for scanner in self._scanners:
            if scanner.want(filename):
                if self._verbose:
                    print("   - {}".format(filename))
                if not file:
                    file = repo.get_contents(filename)
                scanner.check(file.path, file.decoded_content)
