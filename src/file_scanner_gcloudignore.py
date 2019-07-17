from file_scanner import FileScanner
from reporting import ScanResult, ScanResultStatus


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
        return filename == ".gcloudignore" or filename.endswith("/.gcloudignore")

    def check(self, reposlug: str, filename: str, content: str) -> ScanResult:
        result = ScanResult(status=ScanResultStatus.OK, reposlug=reposlug, filename=filename)
        entries = [x.strip() for x in content.splitlines()]
        for r in GCloudIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                result.missings.append(r)
                result.problem.append("{} is not ignored".format(r))
                result.status = ScanResultStatus.ERROR
        if result.status == ScanResultStatus.ERROR:
            result.remedy.append("Add the corresponding ignore entry.")
        return result
