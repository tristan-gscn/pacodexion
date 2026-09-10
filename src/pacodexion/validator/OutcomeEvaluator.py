from __future__ import annotations

from typing import List
from ..cases.TestCase import TestCase
from .ActionDurationTracker import ActionDurationTracker
from .BurnoutTracker import BurnoutTracker
from .ValidationResult import ValidationResult


class OutcomeEvaluator:
    def evaluate(
        self,
        case: TestCase,
        burn: BurnoutTracker,
        actions: ActionDurationTracker,
        n_compiles: int,
        warnings: List[str],
    ) -> ValidationResult:
        if burn.burnouts > 1:
            return ValidationResult(status="KO", detail=f"multiple burned out events: {burn.burnouts}")
        if case.expect_no_burnout and burn.burnouts > 0:
            return ValidationResult(status="KO", detail=f"burnout forbidden for case {case.key}")
        if case.expect_burnout and burn.burnouts == 0:
            return ValidationResult(status="KO", detail=f"expected burnout did not occur for case {case.key}")
        if burn.burnouts == 0 and n_compiles > 0:
            not_done = [str(i) for i, c in actions.compile_counts.items() if c < n_compiles]
            if not_done:
                return ValidationResult(status="KO", detail=f"coders not completed: {','.join(not_done[:20])}")
        if warnings:
            return ValidationResult(status="WARN", detail="\n".join(warnings), warnings=warnings)
        return ValidationResult(status="OK", detail="logs are coherent")
