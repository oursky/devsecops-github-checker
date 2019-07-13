# DevSecOps-ignore
> Check .ignore files from all repository within organization

[![master](https://img.shields.io/badge/travis-master-blue.svg)][travis-url][![TravisCI][travis-image]][travis-url]

## Purpose
A program to scan all repository within organization, that for each repository
if there is ignore files, that file should contains basic ignore entries.

## Using it

#### Create personal access token
1. Visit https://github.com/settings/tokens
2. Generate new token.
3. Tick the `repo` section.

#### Configure
Copy .env.example to .env and edit it.

#### Run the check
```
docker build -t devsecops-ignore https://github.com/oursky/devsecops-ignore.git
docker run -it --rm --env-file .env devsecops-ignore
```

<!-- Markdown link & img dfn's -->
[travis-url]: https://travis-ci.org/oursky/devsecops-ignore
[travis-image]: https://travis-ci.org/oursky/devsecops-ignore.svg?branch=master
