# DevSecOps-ignore
> Check .ignore files from all repository within organization

## Purpose
A program to scan all repository within organization, that for each repository
if there is ignore files, that file should contains basic ignore entries.

## Using it

#### Create personal access token
1. Visit https://github.com/settings/tokens
2. Generate new token.
3. Tick the `repo` section.

#### Run the check
```
docker build -t devsecops-ignore https://github.com/oursky/devsecops-ignore.git
docker run -it --rm -e GITHUB_PERSONAL_TOKEN=xxxxxx devsecops-ignore
```
