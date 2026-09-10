from __future__ import annotations

from typing import List
from .ArgLogicCases import ArgLogicCases
from .ArgSyntaxCases import ArgSyntaxCases
from .TestCase import TestCase


class ErrorCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return ArgSyntaxCases.get_cases() + ArgLogicCases.get_cases()
