from typing import List
from file_scanner import FileScanner
from reporting import ScanResult, ScanResultStatus


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
        return filename == ".gitignore"

    def check(self, reposlug: str, commitsha: str, filesha: str, filename: str,
              content: str, filelist: List[str]) -> ScanResult:
        result = ScanResult(status=ScanResultStatus.OK,
                            reposlug=reposlug,
                            commitsha=commitsha,
                            filesha=filesha,
                            filename=filename,
                            content=content)
        entries = [x.strip() for x in content.splitlines()]
        for r in GitIgnoreFileScanner.REQUIRED_ENTRIES:
            if r not in entries:
                result.missings.append(r)
                result.status = ScanResultStatus.ERROR
        return result
