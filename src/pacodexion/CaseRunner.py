from __future__ import annotations

import subprocess
import time
from typing import Callable, List, Optional, Tuple

from .OutputValidator import OutputValidator
from .TestCase import TestCase

CaseResult = Tuple[TestCase, bool, str]


class CaseRunner:
    def __init__(self) -> None:
        self.validator = OutputValidator()
        self.last_stdout = ""
        self.last_stderr = ""

    def run_all(self, binary: str, cases: List[TestCase], timeout: float) -> Tuple[List[CaseResult], bool]:
        results: List[CaseResult] = []
        any_fail = False
        for case in cases:
            ok, detail = self.run_case(binary, case, timeout)
            results.append((case, ok, detail))
            if not ok:
                any_fail = True
        return results, any_fail

    def run_case(self, binary: str, case: TestCase, timeout: float) -> Tuple[bool, str]:
        return self.run_case_with_progress(binary, case, timeout)

    def run_case_with_progress(
        self,
        binary: str,
        case: TestCase,
        timeout: float,
        on_tick: Optional[Callable[[float], None]] = None,
    ) -> Tuple[bool, str]:
        try:
            process = subprocess.Popen(
                [binary, *case.args],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except OSError as exc:
            self.last_stdout = ""
            self.last_stderr = str(exc)
            return False, f"execution error: {exc}"

        started = time.monotonic()
        stdout_data = ""
        stderr_data = ""
        while True:
            try:
                stdout_data, stderr_data = process.communicate(timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                elapsed = time.monotonic() - started
                if on_tick is not None:
                    on_tick(elapsed)
                if elapsed >= timeout:
                    process.kill()
                    stdout_data, stderr_data = process.communicate()
                    self.last_stdout = stdout_data
                    self.last_stderr = stderr_data
                    return (
                        False,
                        f"timeout after {timeout:.1f}s\n"
                        f"partial_stdout={self._preview(stdout_data or '<empty>')}\n"
                        f"partial_stderr={self._preview(stderr_data or '<empty>')}",
                    )

        self.last_stdout = stdout_data
        self.last_stderr = stderr_data

        completed = subprocess.CompletedProcess(
            args=[binary, *case.args],
            returncode=process.returncode or 0,
            stdout=stdout_data,
            stderr=stderr_data,
        )

        if case.expect_invalid_args:
            return self.validator.validate_error_case(completed)
        return self.validator.validate_regular_case(completed, case.args)

    def get_last_output(self) -> str:
        if self.last_stdout.strip():
            return self.last_stdout
        return self.last_stderr

    def _preview(self, text: str, max_len: int = 240) -> str:
        cleaned = text.replace("\n", "\\n")
        if len(cleaned) <= max_len:
            return cleaned
        return f"{cleaned[:max_len]}...(truncated)"
