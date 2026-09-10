from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from .ParsedLog import ParsedLog
from .ValidationResult import ValidationResult


class ActionDurationTracker:
    def __init__(self, t_compile: int, t_debug: int, t_refactor: int, n_coders: int) -> None:
        self.t_compile = t_compile
        self.t_debug = t_debug
        self.t_refactor = t_refactor
        self.last_compile: Dict[int, int] = {i: 0 for i in range(1, n_coders + 1)}
        self.last_debug: Dict[int, Optional[int]] = {i: None for i in range(1, n_coders + 1)}
        self.last_refactor: Dict[int, Optional[int]] = {i: None for i in range(1, n_coders + 1)}
        self.compile_counts: Dict[int, int] = {i: 0 for i in range(1, n_coders + 1)}

    def on_taken_dongle(self, log: ParsedLog) -> Optional[ValidationResult]:
        refactor_start = self.last_refactor[log.coder]
        if refactor_start is not None:
            waited = log.ts - refactor_start
            if waited < self.t_refactor:
                return ValidationResult(
                    status="KO",
                    detail=(
                        "refactor phase ended too early before taking dongles\n"
                        f"line={log.line_no}\ncoder_id={log.coder}\n"
                        f"expected_min_refactor_ms={self.t_refactor}\n"
                        f"actual_refactor_ms={waited}\nline_value={log.raw}"
                    ),
                )
        return None

    def on_compiling(self, log: ParsedLog) -> None:
        self.compile_counts[log.coder] += 1
        self.last_compile[log.coder] = log.ts
        self.last_debug[log.coder] = None
        self.last_refactor[log.coder] = None

    def on_debugging(self, log: ParsedLog) -> Tuple[Optional[ValidationResult], List[str]]:
        warnings: List[str] = []
        elapsed = log.ts - self.last_compile[log.coder]
        if elapsed < self.t_compile:
            return ValidationResult(
                status="KO",
                detail=(
                    "compile phase ended too early before debugging\n"
                    f"line={log.line_no}\ncoder_id={log.coder}\n"
                    f"expected_min_compile_ms={self.t_compile}\n"
                    f"actual_compile_ms={elapsed}\nline_value={log.raw}"
                ),
            ), warnings
        if elapsed > (self.t_compile * 1.5 + 20):
            drift = elapsed - self.t_compile
            warnings.append(f"line {log.line_no}: coder {log.coder} compile duration ({elapsed}ms) drift +{drift}ms")
        self.last_debug[log.coder] = log.ts
        return None, warnings

    def on_refactoring(self, log: ParsedLog) -> Tuple[Optional[ValidationResult], List[str]]:
        warnings: List[str] = []
        dbg_start = self.last_debug[log.coder]
        if dbg_start is None:
            return ValidationResult(
                status="KO",
                detail=f"refactoring without debugging\nline={log.line_no}\nline_value={log.raw}",
            ), warnings
        elapsed = log.ts - dbg_start
        if elapsed < self.t_debug:
            return ValidationResult(
                status="KO",
                detail=(
                    "debug phase ended too early before refactoring\n"
                    f"line={log.line_no}\ncoder_id={log.coder}\n"
                    f"expected_min_debug_ms={self.t_debug}\n"
                    f"actual_debug_ms={elapsed}\nline_value={log.raw}"
                ),
            ), warnings
        if elapsed > (self.t_debug * 1.5 + 20):
            drift = elapsed - self.t_debug
            warnings.append(f"line {log.line_no}: coder {log.coder} debug duration ({elapsed}ms) drift +{drift}ms")
        self.last_refactor[log.coder] = log.ts
        return None, warnings
