from __future__ import annotations

from typing import List
from .TestCase import TestCase


class ArgLogicCases:
    @staticmethod
    def get_cases() -> List[TestCase]:
        return [
            TestCase(
                "error_arg9", "error_coder",
                ("10", "200", "300", "-400", "500", "5", "10", "edf"),
                description="Negative duration (-400ms)",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_arg10", "error_coder",
                ("too", "10", "200", "300", "400", "500", "5", "10", "edf"),
                description="Too many arguments provided",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_zero_coders", "error_zero_coders",
                ("0", "800", "200", "200", "200", "5", "10", "fifo"),
                description="0 coders must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_neg_coders", "error_neg_coders",
                ("-5", "800", "200", "200", "200", "5", "10", "fifo"),
                description="Negative coders count (-5) must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_caps_scheduler", "error_caps_sched",
                ("4", "800", "200", "200", "200", "5", "10", "FIFO"),
                description="Uppercase scheduler ('FIFO') must be rejected (subject requires 'fifo')",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_empty_arg", "error_empty_arg",
                ("4", "", "200", "200", "200", "5", "10", "fifo"),
                description="Empty string argument ('') must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_spaces", "error_spaces",
                ("4", "800", " 200", "200", "200", "5", "10", "fifo"),
                description="Leading space in argument (' 200') must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_tab", "error_tab",
                ("4", "800", "200\t", "200", "200", "5", "10", "fifo"),
                description="Trailing tab in argument ('200\\t') must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_bad_scheduler", "error_bad_scheduler",
                ("4", "800", "200", "200", "200", "5", "10", "round_robin"),
                description="Unsupported scheduler ('round_robin') must be rejected",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_missing_args", "error_missing_args",
                ("10", "200", "300", "400", "500", "5", "10"),
                description="Missing required scheduler argument",
                expect_invalid_args=True,
            ),
            TestCase(
                "error_no_args", "error_no_args", (),
                description="No arguments provided at all",
                expect_invalid_args=True,
            ),
        ]
