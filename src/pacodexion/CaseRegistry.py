from __future__ import annotations

from typing import Dict, List, Sequence, Tuple

from .TestCase import TestCase


class CaseRegistry:
    def __init__(self) -> None:
        self._cases = self._build_cases()

    def _build_cases(self) -> Dict[str, TestCase]:
        cases = [
            TestCase("1", "basic_fifo", ("4", "800", "200", "200", "200", "5", "10", "fifo")),
            TestCase("2", "basic_edf", ("4", "800", "200", "200", "200", "5", "10", "edf")),
            TestCase("3", "success_fifo", ("10", "10000", "100", "100", "100", "5", "50", "fifo")),
            TestCase("4", "large_edf", ("20", "5000", "500", "500", "500", "10", "100", "edf")),
            TestCase("5", "low_cooldown", ("5", "2000", "100", "100", "100", "20", "1", "fifo")),
            TestCase("6", "long_actions", ("3", "10000", "2000", "2000", "2000", "2", "100", "fifo")),
            TestCase("big", "big_test", ("100", "10000", "66", "24", "87", "10", "10", "fifo")),
            TestCase("starvation", "starvation_case", ("3", "1000", "600", "10", "10", "5", "100", "fifo")),
            TestCase("starvation2", "starvation_case", ("3", "1000", "600", "10", "10", "5", "100", "edf")),
            TestCase("one_compiler_fifo", "one_compiler_fifo", ("1", "1000", "200", "200", "200", "5", "50", "fifo")),
            TestCase("one_compiler_edf", "one_compiler_edf", ("1", "1000", "200", "200", "200", "5", "50", "edf")),
            TestCase("zero_compile", "zero_compiles", ("5", "1000", "200", "200", "200", "0", "10", "fifo")),
            TestCase("immediate_burnout", "immediate_burnout", ("2", "1", "200", "200", "200", "5", "10", "fifo")),
            TestCase("cooldown_hell", "cooldown_hell", ("2", "1000", "100", "100", "100", "5", "2000", "fifo")),
            TestCase("max_coders", "max_coders", ("300", "10000", "100", "100", "100", "5", "10", "edf")),
            TestCase("toomany_compiler", "toomany_compiler", ("999", "1000", "200", "200", "200", "5", "50", "fifo")),
            TestCase("error_arg1", "error_coder", ("banana", "200", "300", "400", "500", "5", "10", "fifo"), True),
            TestCase("error_arg2", "error_coder", ("10", "banana", "300", "400", "500", "5", "10", "fifo"), True),
            TestCase("error_arg3", "error_coder", ("10", "200", "banana", "400", "500", "5", "10", "fifo"), True),
            TestCase("error_arg4", "error_coder", ("10", "200", "300", "banana", "500", "5", "10", "fifo"), True),
            TestCase("error_arg5", "error_coder", ("10", "200", "300", "400", "banana", "5", "10", "fifo"), True),
            TestCase("error_arg6", "error_coder", ("10", "200", "300", "400", "500", "banana", "10", "fifo"), True),
            TestCase("error_arg7", "error_coder", ("10", "200", "300", "400", "500", "5", "banana", "fifo"), True),
            TestCase("error_arg8", "error_coder", ("10", "200", "300", "400", "500", "5", "10", "banana"), True),
            TestCase("error_arg9", "error_coder", ("10", "200", "300", "-400", "500", "5", "10", "edf"), True),
            TestCase("error_arg10", "error_coder", ("too", "10", "200", "300", "400", "500", "5", "10", "edf"), True),
        ]
        return {case.key: case for case in cases}

    def select_cases(self, tokens: Sequence[str]) -> Tuple[List[TestCase], List[str]]:
        if not tokens:
            return list(self._cases.values()), []
        selected: List[TestCase] = []
        unknown: List[str] = []
        for token in tokens:
            case = self._cases.get(token)
            if case is None:
                unknown.append(token)
            else:
                selected.append(case)
        return selected, unknown
