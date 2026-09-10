from __future__ import annotations

import subprocess
from ..cases.TestCase import TestCase
from .CaseArgsParser import CaseArgsParser
from .ErrorCaseValidator import ErrorCaseValidator
from .LogParser import LogParser
from .ProcessSanityChecker import ProcessSanityChecker
from .SimulationValidator import SimulationValidator
from .ValidationResult import ValidationResult


class OutputValidator:
    def __init__(self) -> None:
        self.sanity = ProcessSanityChecker()
        self.args_parser = CaseArgsParser()
        self.log_parser = LogParser()
        self.error_validator = ErrorCaseValidator()
        self.sim_validator = SimulationValidator()

    def validate_error_case(self, completed: subprocess.CompletedProcess[str]) -> ValidationResult:
        return self.error_validator.validate(completed)

    def validate_regular_case(
        self, completed: subprocess.CompletedProcess[str], case: TestCase
    ) -> ValidationResult:
        sanity_res = self.sanity.check(completed)
        if sanity_res is not None:
            return sanity_res

        parsed, err = self.args_parser.parse(case.args)
        if parsed is None:
            return ValidationResult(status="KO", detail=err or "invalid args")

        n_coders, t_burn, t_comp, t_dbg, t_ref, n_comp, cd, _ = parsed
        raw_lines = [ln.strip() for ln in (completed.stdout or "").splitlines() if ln.strip()]

        if not raw_lines:
            if n_comp == 0:
                return ValidationResult(status="OK", detail="no log emitted (compiles_required=0)")
            return ValidationResult(status="KO", detail="empty output while compiles are required")

        parsed_logs, parse_err, parse_warnings = self.log_parser.parse_lines(raw_lines, n_coders)
        if parsed_logs is None:
            return parse_err or ValidationResult(status="KO", detail="parse error")

        params = (n_coders, t_burn, t_comp, t_dbg, t_ref, n_comp, cd)
        return self.sim_validator.simulate(case, parsed_logs, params, parse_warnings)
