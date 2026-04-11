from __future__ import annotations

from pathlib import Path

from .TestCase import TestCase


class KoTraceWriter:
    def __init__(self, trace_dir: str = "traces") -> None:
        self.trace_path = Path(trace_dir)

    def write(self, case: TestCase, codexion_output: str, detail: str) -> Path:
        self.trace_path.mkdir(parents=True, exist_ok=True)
        file_path = self.trace_path / self._file_name(case)
        content = self._build_content(codexion_output, detail)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    def _file_name(self, case: TestCase) -> str:
        safe_name = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in case.name)
        return f"{case.key}_{safe_name}.log"

    def _build_content(self, codexion_output: str, detail: str) -> str:
        lines = codexion_output.splitlines()
        if not lines:
            return "PROBLEM HERE >>>\n"

        line_no = self._extract_field(detail, "line")
        idx = 0
        if line_no is not None and line_no.isdigit():
            candidate = int(line_no) - 1
            if 0 <= candidate < len(lines):
                idx = candidate
        lines[idx] = f"PROBLEM HERE >>> {lines[idx]}"
        return "\n".join(lines) + "\n"

    def _extract_field(self, detail: str, key: str) -> str | None:
        prefix = f"{key}="
        for line in detail.splitlines():
            if line.startswith(prefix):
                return line[len(prefix) :]
        return None
