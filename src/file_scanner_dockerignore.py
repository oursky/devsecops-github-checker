import re
from typing import List
from file_scanner import FileScanner
from reporting import ScanResult, ScanResultStatus


class DockerIgnoreFileScanner(FileScanner):
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
        ["*.gpg", ".*\\.gpg$"],
        [".blackbox/", "\\.blackbox/*"],
        [".keyring/", "\\.keyring/*"],
        ["keyring/", "keyring/*"],
        [".keyrings/", "\\.keyrings/*"],
        ["keyrings/", "keyrings/*"],
    ]

    def want(self, filename: str) -> bool:
        return filename == ".dockerignore" or filename.endswith("/.dockerignore")

    def _contain_file(self, filelist: List[str], pattern: str) -> bool:
        checker = re.compile(pattern)
        for file in filelist:
            if checker.match(file):
                return True
        return False

    def check(self, reposlug: str, filename: str, content: str, filelist: List[str]) -> ScanResult:
        result = ScanResult(status=ScanResultStatus.OK, reposlug=reposlug, filename=filename)
        entries = [x.strip() for x in content.splitlines()]
        for r in DockerIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                result.missings.append(r)
                result.problem.append("{} is not ignored".format(r))
                result.status = ScanResultStatus.ERROR
        for r, pattern in DockerIgnoreFileScanner.CONDITIONAL_ENTRIES:
            if r not in entries and self._contain_file(filelist, pattern):
                result.missings.append(r)
                result.problem.append("{} is not ignored".format(r))
                result.status = ScanResultStatus.ERROR
        if result.status == ScanResultStatus.ERROR:
            result.remedy.append("Add the corresponding ignore entry.")
        return result
