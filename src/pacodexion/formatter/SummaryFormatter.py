from __future__ import annotations

from typing import Iterable, Tuple
from ..cases.TestCase import TestCase
from ..validator.ValidationResult import ValidationResult
from .AnsiStyler import AnsiStyler

CaseResult = Tuple[TestCase, ValidationResult]


class SummaryFormatter:
    def __init__(self, styler: AnsiStyler) -> None:
        self.styler = styler

    def render(self, results: Iterable[CaseResult]) -> str:
        res_list = list(results)
        total = len(res_list)
        failed = sum(1 for _, res in res_list if res.is_ko)
        warned = sum(1 for _, res in res_list if res.is_warn)
        passed = total - failed

        if failed == 0:
            status = self.styler.color("passed", self.styler.GREEN)
            detail = f" ({warned} with warnings)" if warned > 0 else ""
            return f"Summary: {passed}/{total} {status}{detail}"

        ko_str = self.styler.color(f"{failed} failed", self.styler.RED)
        warn_str = f", {warned} with warnings" if warned > 0 else ""
        return f"Summary: {passed}/{total} passed{warn_str}, {ko_str}"
