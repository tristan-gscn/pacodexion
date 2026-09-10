from __future__ import annotations

import subprocess
from .ProcessSanityChecker import ProcessSanityChecker
from .ValidationResult import ValidationResult


class ErrorCaseValidator:
    def __init__(self) -> None:
        self.sanity = ProcessSanityChecker()

    def validate(self, completed: subprocess.CompletedProcess[str]) -> ValidationResult:
        merged = (completed.stdout or "") + "\n" + (completed.stderr or "")
        lines = [ln.strip() for ln in merged.splitlines() if ln.strip()]
        error_keywords = ("error", "invalid", "usage", "incorrect", "bad", "wrong")
        has_error_word = any(
            any(word in line.lower() for word in error_keywords)
            for line in lines
        )
        if completed.returncode != 0:
            return ValidationResult(
                status="OK",
                detail="invalid argument rejection detected (non-zero exit code)",
            )
        if has_error_word:
            warning = "invalid arguments rejected with message but program exited with returncode 0"
            return ValidationResult(status="WARN", detail=warning, warnings=[warning])
        return ValidationResult(
            status="KO",
            detail=(
                "expected invalid-argument rejection but command looked successful\n"
                f"return_code={completed.returncode}\n"
                f"stdout={self.sanity.preview(completed.stdout or '<empty>')}\n"
                f"stderr={self.sanity.preview(completed.stderr or '<empty>')}"
            ),
        )
