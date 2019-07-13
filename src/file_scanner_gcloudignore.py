from file_scanner import FileScanner


class GCloudIgnoreFileScanner(FileScanner):
    REQUIRED_ENTRIES = [
        ".git/",
        ".DS_Store",
        "*.pem",
        "*.cer",
        "*.cert",
        "*.p12",
        "*.pfx",
        "*.key",
        ".env",
        "docker-compose.override.yml",

        ".blackbox/",
        "*.gpg",
    ]

    def want(self, filename: str) -> bool:
        return filename.endswith(".gcloudignore")

    def check(self, filename: str, content: str) -> bool:
        result = True
        entries = [x.strip() for x in content.splitlines()]
        for r in GCloudIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                print("     [E] Missing {}".format(r))
                result = False
        return result
