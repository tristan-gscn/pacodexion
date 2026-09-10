from __future__ import annotations

import subprocess
import time
from typing import Callable, List, Optional
from ..cases.TestCase import TestCase
from ..validator.OutputValidator import OutputValidator
from ..validator.ValidationResult import ValidationResult


class CaseRunner:
    def __init__(self, validator: Optional[OutputValidator] = None) -> None:
        self.validator = validator or OutputValidator()
        self._last_output = ""

    def get_last_output(self) -> str:
        return self._last_output

    def run_case_with_progress(
        self,
        binary: str,
        case: TestCase,
        timeout: float,
        on_tick: Optional[Callable[[float], None]] = None,
    ) -> ValidationResult:
        cmd: List[str] = [binary, *case.args]
        start_time = time.monotonic()

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        while True:
            ret = proc.poll()
            if ret is not None:
                stdout, stderr = proc.communicate()
                self._last_output = stdout
                completed = subprocess.CompletedProcess(cmd, ret, stdout, stderr)
                if case.expect_invalid_args:
                    return self.validator.validate_error_case(completed)
                return self.validator.validate_regular_case(completed, case)

            elapsed = time.monotonic() - start_time
            if on_tick:
                on_tick(elapsed)

            if elapsed > timeout:
                proc.kill()
                stdout, stderr = proc.communicate()
                self._last_output = stdout
                return ValidationResult(
                    status="KO",
                    detail=f"test timed out after {timeout}s (deadlock or infinite loop)",
                )

            time.sleep(0.05)
