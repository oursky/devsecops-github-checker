import signal
import sys
from arguments import Arguments
from crawler import GithubCrawler


def signal_handler(sig, frame):
    print("You pressed Ctrl-C!")
    sys.exit(0)


def main():
    args = Arguments()
    if not args.load():
        exit(0)
    g = GithubCrawler(args.github_token, args.organization, verbose=args.verbose)
    g.scan()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
