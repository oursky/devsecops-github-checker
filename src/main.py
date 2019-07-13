from environs import Env
from crawler import GithubCrawler


def main():
    env = Env()
    env.read_env()

    GITHUB_TOKEN = env.str('GITHUB_PERSONAL_TOKEN')
    ORGANIZATION = env.str('GITHUB_ORGANIZATION', None)
    g = GithubCrawler(GITHUB_TOKEN, ORGANIZATION)
    g.scan()


if __name__ == "__main__":
    main()
