from __future__ import annotations

import os
import re
from typing import List, Optional
from ..cases.TestCase import TestCase


class TraceWriter:
    def __init__(self, base_dir: str = "traces") -> None:
        self.base_dir = base_dir

    def write(
        self,
        case: TestCase,
        output: str,
        detail: str,
        *,
        subdir: str = "ko",
        highlight_failure: bool = True,
        warnings: Optional[List[str]] = None,
    ) -> str:
        target_dir = os.path.join(self.base_dir, subdir)
        os.makedirs(target_dir, exist_ok=True)
        filename = os.path.join(target_dir, f"{case.key}_{case.name}.trace")

        fail_line = self._find_first_line_no(detail)
        warn_lines = [self._find_first_line_no(w) for w in (warnings or [])]

        annotated: List[str] = []
        for idx, line in enumerate(output.splitlines(), start=1):
            if highlight_failure and fail_line is not None and idx == fail_line:
                annotated.append(f">>> PROBLEM HERE >>> {line}")
            elif idx in warn_lines:
                annotated.append(f">>> WARNING HERE >>> {line}")
            else:
                annotated.append(line)

        body = "\n".join(annotated)
        content = (
            f"Case: {case.key} ({case.name})\n"
            f"Args: {' '.join(case.args)}\n"
            f"Diagnostics:\n{detail}\n\n"
            f"=== Output ===\n{body}\n"
        )
        with open(filename, "w", encoding="utf-8") as file:
            file.write(content)
        return filename

    def _find_first_line_no(self, text: str) -> Optional[int]:
        match = re.search(r"\bline(?:_no)?=(\d+)\b", text) or re.search(r"\bline\s+(\d+)\b", text)
        return int(match.group(1)) if match else None
