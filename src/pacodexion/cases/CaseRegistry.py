from __future__ import annotations

from typing import Dict, List, Sequence, Tuple
from .BurnoutCases import BurnoutCases
from .ErrorCases import ErrorCases
from .NominalCases import NominalCases
from .StressCases import StressCases
from .TestCase import TestCase


class CaseRegistry:
    def __init__(self) -> None:
        all_cases = (
            NominalCases.get_cases()
            + BurnoutCases.get_cases()
            + StressCases.get_cases()
            + ErrorCases.get_cases()
        )
        self._cases: Dict[str, TestCase] = {case.key: case for case in all_cases}

    def all_cases(self) -> List[TestCase]:
        return list(self._cases.values())

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
