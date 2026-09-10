from __future__ import annotations

from typing import List
from .TestCase import TestCase


class ArgSyntaxCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return [
            TestCase(
                "error_arg1", "error_coder",
                ("banana", "200", "300", "400", "500", "5", "10", "fifo"),
                description="Invalid number_of_coders (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg2", "error_coder",
                ("10", "banana", "300", "400", "500", "5", "10", "fifo"),
                description="Invalid time_to_burnout (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg3", "error_coder",
                ("10", "200", "banana", "400", "500", "5", "10", "fifo"),
                description="Invalid time_to_compile (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg4", "error_coder",
                ("10", "200", "300", "banana", "500", "5", "10", "fifo"),
                description="Invalid time_to_debug (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg5", "error_coder",
                ("10", "200", "300", "400", "banana", "5", "10", "fifo"),
                description="Invalid time_to_refactor (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg6", "error_coder",
                ("10", "200", "300", "400", "500", "banana", "10", "fifo"),
                description="Invalid number_of_compiles (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg7", "error_coder",
                ("10", "200", "300", "400", "500", "5", "banana", "fifo"),
                description="Invalid dongle_cooldown (non-numeric string)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg8", "error_coder",
                ("10", "200", "300", "400", "500", "5", "10", "banana"),
                description="Invalid scheduler name ('banana')",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_float", "error_float",
                ("4", "800.5", "200", "200", "200", "5", "10", "fifo"),
                description="Floating point argument (800.5) must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_overflow", "error_overflow",
                ("4", "999999999999999999999999999999", "200", "200", "200", "5", "10", "fifo"),
                description="Integer overflow value must be safely rejected",
                expect_invalid_args=True,
            ),
        ]
