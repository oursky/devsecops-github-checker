from typing import Optional
from github import (
    Github,
    NamedUser,
    Organization,
    Repository,
    ContentFile,
)


class GithubCrawler:
    def __init__(self, access_token: str, organization: Optional[str] = None):
        self._github = Github(access_token)
        self._organization = organization

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
        contents = repo.get_contents("")
        while contents:
            file = contents.pop(0)
            if file.type == "dir":
                contents.extend(repo.get_contents(file.path))
            else:
                self._scan_file(user, org, repo, file)

    def _scan_file(self, user: NamedUser, org: Organization, repo: Repository, file: ContentFile) -> None:
        print("{}/{} /{}/{}".format(org.login, repo.name, file.path, file.name))
