from __future__ import annotations

from typing import Dict, Optional
from .ParsedLog import ParsedLog
from .ValidationResult import ValidationResult


class StateSequenceTracker:
    def __init__(self, n_coders: int) -> None:
        self.n_coders = n_coders
        self.last_state: Dict[int, str] = {i: "init" for i in range(1, n_coders + 1)}
        self.taken_counts: Dict[int, int] = {i: 0 for i in range(1, n_coders + 1)}

    def check_transition(self, log: ParsedLog) -> Optional[ValidationResult]:
        prev = self.last_state[log.coder]
        curr = log.state
        count = self.taken_counts[log.coder]

        invalid = False
        if curr != "burned out":
            if prev == "init":
                invalid = (curr != "has taken a dongle")
            elif prev == "has taken a dongle":
                if curr == "has taken a dongle":
                    invalid = (count >= 2)
                else:
                    invalid = (curr != "is compiling" or count != 2)
            elif prev == "is compiling":
                invalid = (curr != "is debugging")
            elif prev == "is debugging":
                invalid = (curr != "is refactoring")
            elif prev == "is refactoring":
                invalid = (curr != "has taken a dongle")

        if invalid:
            return ValidationResult(
                status="KO",
                detail=(
                    "invalid state transition sequence\n"
                    f"line={log.line_no}\n"
                    f"coder_id={log.coder}\n"
                    f"previous_state={prev}\n"
                    f"current_state={curr}\n"
                    f"line_value={log.raw}"
                ),
            )

        if curr == "has taken a dongle":
            self.taken_counts[log.coder] += 1
        elif curr == "is compiling":
            self.taken_counts[log.coder] = 0

        self.last_state[log.coder] = curr
        return None
