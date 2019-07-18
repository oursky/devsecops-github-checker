from typing import List, TextIO
from results import ScanResultStatus, ScanResult, ScanResults


class Reporting():
    def __init__(self, verbose: bool = False):
        self._verbose = verbose
        self._results = {}
        self._warnings = 0
        self._errors = 0

    def print(self, results: ScanResults) -> None:
        with open('result.txt', 'a') as logfile:
            msg = "\nSummary: {total} repo checked, {warn} warnings, {err} errors".format(
                total=results.total,
                warn=results.warnings,
                err=results.errors)
            print(msg)
            print(msg, file=logfile)
            for reposlug in results.results:
                if not results.have_problem(reposlug):
                    continue
                self._emit_log(reposlug, results.results[reposlug], logfile)

    def _emit_log(self, reposlug: str, results: List[ScanResult], logfile: TextIO) -> None:
        message = ""
        for result in results:
            if result.status == ScanResultStatus.OK:
                continue
            item = "[{status}] {slug}: {file}\n    {problem}\n\n".format(
                status=result.status.value,
                slug=result.reposlug,
                file=result.filename,
                problem="\n    ".join(result.missings))
            message = message + item
        if self._verbose:
            print(message)
        print(message, file=logfile)
