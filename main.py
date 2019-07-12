import os
from github import Github

GITHUB_TOKEN=os.environ.pop('GITHUB_PERSONAL_TOKEN', None)
g = Github(GITHUB_TOKEN)
for repo in g.get_user().get_repos():
    print(repo.name)
