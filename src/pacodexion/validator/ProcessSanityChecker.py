from __future__ import annotations

import subprocess
from typing import Optional
from .ValidationResult import ValidationResult


class ProcessSanityChecker:
    @staticmethod
    def preview(text: str, max_len: int = 240) -> str:
        cleaned = text.replace("\n", "\\n")
        if len(cleaned) <= max_len:
            return cleaned
        return f"{cleaned[:max_len]}...(truncated)"

    def check(self, completed: subprocess.CompletedProcess[str]) -> Optional[ValidationResult]:
        stderr_content = (completed.stderr or "").strip()
        low_stderr = stderr_content.lower()

        if "threadsanitizer" in low_stderr or "data race" in low_stderr:
            return ValidationResult(
                status="KO",
                detail=f"ThreadSanitizer detected concurrency error:\n{stderr_content}",
            )
        if "addresssanitizer" in low_stderr:
            return ValidationResult(
                status="KO",
                detail=f"AddressSanitizer detected memory error:\n{stderr_content}",
            )
        if "helgrind" in low_stderr:
            return ValidationResult(
                status="KO",
                detail=f"Helgrind detected concurrency error:\n{stderr_content}",
            )

        if completed.returncode != 0:
            sig_name = ""
            rc = completed.returncode
            if rc in (-11, 139):
                sig_name = " [Segmentation fault - SIGSEGV]"
            elif rc in (-6, 134):
                sig_name = " [Aborted - SIGABRT]"
            elif rc in (-10, 138):
                sig_name = " [Bus error - SIGBUS]"
            elif rc in (-15, 143):
                sig_name = " [Terminated - SIGTERM]"
            elif rc == 66:
                sig_name = " [ThreadSanitizer exit]"

            return ValidationResult(
                status="KO",
                detail=(
                    f"process crashed or exited with non-zero code{sig_name}\n"
                    f"return_code={completed.returncode}\n"
                    f"stdout={self.preview(completed.stdout or '<empty>')}\n"
                    f"stderr={self.preview(stderr_content or '<empty>')}"
                ),
            )
        return None
