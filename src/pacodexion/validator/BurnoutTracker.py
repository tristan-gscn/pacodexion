from __future__ import annotations

from typing import List, Optional, Tuple
from .ParsedLog import ParsedLog
from .ValidationResult import ValidationResult


class BurnoutTracker:
    def __init__(self, t_burnout: int) -> None:
        self.t_burnout = t_burnout
        self.burnouts = 0
        self.burnout_coder: Optional[int] = None

    def on_burnout(
        self,
        log: ParsedLog,
        last_compile_start: int,
        idx: int,
        all_logs: List[ParsedLog],
    ) -> Tuple[Optional[ValidationResult], List[str]]:
        warnings: List[str] = []
        self.burnouts += 1
        self.burnout_coder = log.coder

        deadline = last_compile_start + self.t_burnout
        lateness = log.ts - deadline

        if lateness < 0:
            return ValidationResult(
                status="KO",
                detail=(
                    "burned out before deadline\n"
                    f"line={log.line_no}\ncoder_id={log.coder}\n"
                    f"deadline_ms={deadline}\nactual_burnout_ms={log.ts}\nline_value={log.raw}"
                ),
            ), warnings

        if lateness > 25:
            return ValidationResult(
                status="KO",
                detail=(
                    "burnout detection delayed beyond 25ms tolerance\n"
                    f"line={log.line_no}\ncoder_id={log.coder}\n"
                    f"deadline_ms={deadline}\nactual_burnout_ms={log.ts}\n"
                    f"delay_ms={lateness}\ntarget_delay_ms=<=10 (tolerance <=25ms)\n"
                    f"line_value={log.raw}"
                ),
            ), warnings

        if lateness > 10:
            warnings.append(
                f"line {log.line_no}: coder {log.coder} burnout announced with {lateness}ms delay "
                "(spec requires <=10ms, accepted within OS scheduling tolerance <=25ms)"
            )

        # Check for post-mortem actions
        for subsequent in all_logs[idx:]:
            if subsequent.ts > log.ts:
                return ValidationResult(
                    status="KO",
                    detail=(
                        "simulation actions logged after burnout event\n"
                        f"line={log.line_no}\nburned_out_line={log.raw}\n"
                        f"next_line={subsequent.raw}"
                    ),
                ), warnings

        return None, warnings
