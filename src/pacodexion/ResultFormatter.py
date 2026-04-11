from __future__ import annotations

from typing import Iterable, Tuple

from .TestCase import TestCase

CaseResult = Tuple[TestCase, bool, str]


class ResultFormatter:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    CYAN = "\033[36m"

    def __init__(self, use_color: bool) -> None:
        self.use_color = use_color

    def _color(self, text: str, color: str) -> str:
        if not self.use_color:
            return text
        return f"{color}{text}{self.RESET}"

    def _bold(self, text: str) -> str:
        if not self.use_color:
            return text
        return f"{self.BOLD}{text}{self.RESET}"

    def render_result(self, case: TestCase, ok: bool, detail: str) -> str:
        raw_status = "OK" if ok else "KO"
        color = self.GREEN if ok else self.RED
        status = self._color(raw_status, color)
        header = f"[{status}] {case.key} ({case.name})"
        if ok:
            return header
        trace = self._color(detail, self.RED)
        return f"{header}\n{trace}\n"

    def render_results(self, results: Iterable[CaseResult]) -> Iterable[str]:
        for case, ok, detail in results:
            yield self.render_result(case, ok, detail)

    def render_summary(self, results: Iterable[CaseResult]) -> str:
        result_list = list(results)
        passed = sum(1 for _, ok, _ in result_list if ok)
        total = len(result_list)
        summary = f"Summary: {passed}/{total} passed"
        if passed == total:
            return self._bold(self._color(summary, self.GREEN))
        return self._bold(self._color(summary, self.RED))

    def render_running(self, case: TestCase, frame: str) -> str:
        if self.use_color:
            return f"\r{self._color(frame, self.CYAN)} Running {case.key} ({case.name})..."
        return f"Running {case.key} ({case.name})..."
