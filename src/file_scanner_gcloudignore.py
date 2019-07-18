import re
from typing import List
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
    ]
    CONDITIONAL_ENTRIES = [
        ["*.gpg", r'.*\.gpg$'],
        [".blackbox/", r'\.blackbox/.*'],
        [".keyring/", r'\.keyring/.*'],
        ["keyring/", r'keyring/.*'],
        [".keyrings/", r'\.keyrings/.*'],
        ["keyrings/", r'keyrings/.*'],
    ]

    def want(self, filename: str) -> bool:
        return filename == ".gcloudignore" or filename.endswith("/.gcloudignore")

    def _contain_file(self, filelist: List[str], pattern: str) -> bool:
        checker = re.compile(pattern)
        for file in filelist:
            if checker.match(file):
                return True
        return False

    def check(self, reposlug: str, filename: str, content: str, filelist: List[str]) -> ScanResult:
        result = ScanResult(status=ScanResultStatus.OK, reposlug=reposlug, filename=filename)
        entries = [x.strip() for x in content.splitlines()]
        for r in GCloudIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                result.missings.append(r)
                result.status = ScanResultStatus.ERROR
        for r, pattern in GCloudIgnoreFileScanner.CONDITIONAL_ENTRIES:
            if r not in entries and self._contain_file(filelist, pattern):
                result.missings.append(r)
                result.status = ScanResultStatus.ERROR
        return result
