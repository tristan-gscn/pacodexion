from __future__ import annotations

from typing import List
from .TestCase import TestCase


class BurnoutCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return [
            TestCase(
                "starvation", "starvation_case",
                ("3", "1000", "600", "10", "10", "5", "100", "fifo"),
                description="3 coders with 600ms compile: starves neighbors, burnout expected (FIFO)",
                expect_burnout=True,
            ),
            TestCase(
                "starvation2", "starvation_case",
                ("3", "1000", "600", "10", "10", "5", "100", "edf"),
                description="3 coders with 600ms compile: starves neighbors, burnout expected (EDF)",
                expect_burnout=True,
            ),
            TestCase(
                "one_compiler_fifo", "one_compiler_fifo",
                ("1", "1000", "200", "200", "200", "5", "50", "fifo"),
                description="1 coder only: cannot acquire 2 dongles, burnout expected (FIFO)",
                expect_burnout=True,
            ),
            TestCase(
                "one_compiler_edf", "one_compiler_edf",
                ("1", "1000", "200", "200", "200", "5", "50", "edf"),
                description="1 coder only: cannot acquire 2 dongles, burnout expected (EDF)",
                expect_burnout=True,
            ),
            TestCase(
                "immediate_burnout", "immediate_burnout",
                ("2", "1", "200", "200", "200", "5", "10", "fifo"),
                description="1ms burnout: coder must burn out immediately (<=10ms delay)",
                expect_burnout=True,
            ),
            TestCase(
                "cooldown_hell", "cooldown_hell",
                ("2", "1000", "100", "100", "100", "5", "2000", "fifo"),
                description="2000ms cooldown: dongles unavailable in time, burnout expected",
                expect_burnout=True,
            ),
        ]
