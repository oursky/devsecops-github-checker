from environs import Env


class Arguments():
    def __init__(self):
        self.github_token = None
        self.organization = None
        self.verbose = False
        self.create_git_issue = False

    def load(self):
        env = Env()
        env.read_env()
        self.github_token = env.str('GITHUB_PERSONAL_TOKEN')
        self.organization = env.str('GITHUB_ORGANIZATION', None)
        self.verbose = env.bool("VERBOSE", False)
        self.create_git_issue = env.bool("CREATE_GIT_ISSUE", False)
        return True
