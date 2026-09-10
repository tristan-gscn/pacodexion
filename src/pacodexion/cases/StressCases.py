from __future__ import annotations

from typing import List
from .TestCase import TestCase


class StressCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return [
            TestCase(
                "big", "big_test",
                ("100", "10000", "66", "24", "87", "10", "10", "fifo"),
                description="Concurrency stress test with 100 simultaneous coders",
                expect_no_burnout=True,
            ),
            TestCase(
                "max_coders", "max_coders",
                ("300", "10000", "100", "100", "100", "5", "10", "edf"),
                description="Scalability test with 300 coders under EDF scheduler",
                expect_no_burnout=True,
            ),
            TestCase(
                "toomany_compiler", "toomany_compiler",
                ("999", "1000", "200", "200", "200", "5", "50", "fifo"),
                description="Extreme thread contention (999 threads) to catch data races",
            ),
        ]
