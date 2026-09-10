from __future__ import annotations

from typing import List
from .TestCase import TestCase


class NominalCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return [
            TestCase(
                "1", "basic_fifo",
                ("4", "800", "200", "200", "200", "5", "10", "fifo"),
                description="4 coders, balanced cycles, FIFO scheduler (nominal run)",
                expect_no_burnout=True,
            ),
            TestCase(
                "2", "basic_edf",
                ("4", "800", "200", "200", "200", "5", "10", "edf"),
                description="4 coders, balanced cycles, EDF scheduler (nominal run)",
                expect_no_burnout=True,
            ),
            TestCase(
                "3", "success_fifo",
                ("10", "10000", "100", "100", "100", "5", "50", "fifo"),
                description="10 coders, 5 required compiles, verifies successful completion",
                expect_no_burnout=True,
            ),
            TestCase(
                "4", "large_edf",
                ("20", "5000", "500", "500", "500", "10", "100", "edf"),
                description="20 coders with 500ms actions under EDF scheduler",
                expect_no_burnout=True,
            ),
            TestCase(
                "5", "low_cooldown",
                ("5", "2000", "100", "100", "100", "20", "1", "fifo"),
                description="5 coders with minimal 1ms cooldown to test fast handovers",
                expect_no_burnout=True,
            ),
            TestCase(
                "6", "long_actions",
                ("3", "4000", "600", "600", "600", "2", "50", "fifo"),
                description="3 coders with long action phases (600ms each)",
                expect_no_burnout=True,
            ),
            TestCase(
                "zero_compile", "zero_compiles",
                ("5", "1000", "200", "200", "200", "0", "10", "fifo"),
                description="0 compiles required: coders must not compile, clean exit",
                expect_no_burnout=True,
            ),
            TestCase(
                "tight_timings", "tight_timings",
                ("4", "410", "100", "100", "100", "5", "5", "edf"),
                description="Tight margins (410ms burnout vs 300ms cycle): tests timing precision",
                expect_no_burnout=True,
            ),
        ]
