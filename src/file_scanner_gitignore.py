from file_scanner import FileScanner


class GitIgnoreFileScanner(FileScanner):
    REQUIRED_ENTRIES = [
        ".DS_Store",
        "*.pem",
        "*.cer",
        "*.cert",
        "*.p12",
        "*.pfx",
        "*.key",
        ".env",
        "docker-compose.override.yml",
    ]

    def want(self, filename: str) -> bool:
        return filename.endswith(".gitignore")

    def check(self, filename: str, content: str) -> bool:
        result = True
        entries = [x.strip() for x in content.splitlines()]
        for r in GitIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                print("     [E] Missing {}".format(r))
                result = False
        return result
