from environs import Env
import getopt


class Arguments():
    def __init__(self):
        self.help = False
        self.github_token = None
        self.organization = None
        self.verbose = False
        self.create_issue = False
        self.create_pr = False

    def load(self, args):
        env = Env()
        env.read_env()
        self.github_token = env.str('GITHUB_PERSONAL_TOKEN', None)
        self.organization = env.str('GITHUB_ORGANIZATION', None)
        self.verbose = env.bool("VERBOSE", False)
        self.create_issue = env.bool("CREATE_ISSUE", False)
        self.create_pr = env.bool("CREATE_PR", False)
        # command line arg override
        try:
            opts, args = getopt.getopt(args,
                                       "hv",
                                       ["help",
                                        "verbose",
                                        "create-issue",
                                        "create-pr"])
            for o, a in opts:
                if o in ("-v", "--verbose"):
                    self.verbose = True
                elif o in ("-h", "--help"):
                    self.help = True
                elif o in ("--create-issue"):
                    self.create_issue = True
                elif o in ("--create-pr"):
                    self.create_pr = True
        except getopt.GetoptError:
            pass

        if not self.github_token:
            print("GITHUB_PERSONAL_TOKEN not configured, please set it on .env")
            return False
        return True

    def print_help(self):
        print("usage: python main.py [-h] -[v] [--create-issue] [--create-pr]")
        print("  -h              Show this help")
        print("  -v              Verbose")
        print("  --create-issue  Automatic create github issue")
        print("  --create-pr     Generate autofix pull request")
