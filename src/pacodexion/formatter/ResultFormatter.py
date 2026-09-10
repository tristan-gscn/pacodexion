from __future__ import annotations

from typing import Iterable, Tuple
from ..cases.TestCase import TestCase
from ..validator.ValidationResult import ValidationResult
from .AnsiStyler import AnsiStyler
from .CaseListFormatter import CaseListFormatter
from .SummaryFormatter import SummaryFormatter

CaseResult = Tuple[TestCase, ValidationResult]


class ResultFormatter:
    def __init__(self, use_color: bool = True) -> None:
        self.styler = AnsiStyler(use_color=use_color)
        self.list_formatter = CaseListFormatter(self.styler)
        self.summary_formatter = SummaryFormatter(self.styler)

    def render_result(self, case: TestCase, result: ValidationResult) -> str:
        args_str = " ".join(case.args) if case.args else "<no arguments>"
        if result.is_ko:
            status = self.styler.color("KO", self.styler.RED)
            header = f"[{status}] {case.key} ({case.name})"
            lines = [header, f"  arguments: {args_str}"]
            for d_line in result.detail.splitlines():
                lines.append(f"  {self.styler.color(d_line, self.styler.RED)}")
            return "\n".join(lines)
        elif result.is_warn:
            status = self.styler.color("WARN", self.styler.YELLOW)
            header = f"[{status}] {case.key} ({case.name})"
            lines = [header, f"  arguments: {args_str}"]
            for w in result.warnings:
                lines.append(f"  {self.styler.color(w, self.styler.YELLOW)}")
            return "\n".join(lines)
        else:
            status = self.styler.color("OK", self.styler.GREEN)
            return f"[{status}] {case.key} ({case.name})"

    def render_running(self, case: TestCase, frame: str) -> str:
        running = self.styler.color(f"Running {case.key} ({case.name})...", self.styler.CYAN)
        return f"\r{frame} {running}"

    def render_cases_list(self, cases: Iterable[TestCase]) -> str:
        return self.list_formatter.render(cases)

    def render_summary(self, results: Iterable[CaseResult]) -> str:
        return self.summary_formatter.render(results)
