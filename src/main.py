from github import Github
from arguments import Arguments
from crawler import GithubCrawler
from reporting import Reporting


def main():
    print("== DevSecOps: ignore ==\nScan github repositories for misconfigured ignore files.\n")

    args = Arguments()
    if not args.load():
        exit(0)
    github = Github(args.github_token)
    reporting = Reporting(github, verbose=args.verbose, create_git_issue=args.create_git_issue)
    g = GithubCrawler(github, args.organization, reporting=reporting)
    try:
        g.scan()
    except KeyboardInterrupt:
        print("\n\n*****************************\n[W] User aborted with CTRL-C.\n*****************************\n")
        pass
    reporting.print()


if __name__ == "__main__":
    main()
