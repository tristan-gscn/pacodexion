from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple
from .ParsedLog import ParsedLog
from .ValidationResult import ValidationResult


class DongleTracker:
    def __init__(self, n_coders: int, dongle_cooldown: int) -> None:
        self.n_coders = n_coders
        self.dongle_cooldown = dongle_cooldown
        self.compiling_coders: Set[int] = set()
        self.cooldown_until: Dict[int, int] = {d: 0 for d in range(1, n_coders + 1)}
        self.last_released_by: Dict[int, int] = {d: 0 for d in range(1, n_coders + 1)}

    def on_compiling(self, log: ParsedLog) -> Tuple[Optional[ValidationResult], List[str]]:
        warnings: List[str] = []
        n = self.n_coders
        coder = log.coder
        ts = log.ts

        if n == 1:
            return ValidationResult(
                status="KO",
                detail=f"coder 1 cannot compile with only 1 dongle on table\nline={log.line_no}\nvalue={log.raw}",
            ), warnings

        left = n if coder == 1 else coder - 1
        right = 1 if coder == n else coder + 1

        if left in self.compiling_coders or right in self.compiling_coders:
            adj = left if left in self.compiling_coders else right
            side = "left" if adj == left else "right"
            return ValidationResult(
                status="KO",
                detail=(
                    "concurrency violation: two adjacent coders compiling simultaneously\n"
                    f"line={log.line_no}\ncoder={coder} started compiling while {side} neighbor "
                    f"{adj} is already compiling\nline_value={log.raw}"
                ),
            ), warnings

        if len(self.compiling_coders) >= n // 2:
            return ValidationResult(
                status="KO",
                detail=(
                    "concurrency violation: too many simultaneous compiling coders\n"
                    f"line={log.line_no}\nattempting with {len(self.compiling_coders) + 1} coders, "
                    f"max is {n // 2}\nline_value={log.raw}"
                ),
            ), warnings

        for d_id, side in [(left, "left"), (coder, "right")]:
            if ts < self.cooldown_until[d_id]:
                diff = self.cooldown_until[d_id] - ts
                if diff > 10:
                    return ValidationResult(
                        status="KO",
                        detail=(
                            "cooldown violation: dongle used before cooldown expiration\n"
                            f"line={log.line_no}\ncoder {coder} is compiling using dongle {d_id} at {ts}ms, "
                            f"but cooldown is active until {self.cooldown_until[d_id]}ms "
                            f"({diff}ms too early, last released by coder {self.last_released_by[d_id]})\n"
                            f"line_value={log.raw}"
                        ),
                    ), warnings
                warnings.append(
                    f"line {log.line_no}: coder {coder} compiled using {side} dongle {d_id} "
                    f"{diff}ms before cooldown expiration "
                    f"(active until {self.cooldown_until[d_id]}ms, accepted under OS jitter <=10ms)"
                )

        self.compiling_coders.add(coder)
        return None, warnings

    def on_debugging(self, log: ParsedLog) -> None:
        self.compiling_coders.discard(log.coder)
        if self.n_coders > 1:
            left = self.n_coders if log.coder == 1 else log.coder - 1
            right = log.coder
            self.cooldown_until[left] = log.ts + self.dongle_cooldown
            self.cooldown_until[right] = log.ts + self.dongle_cooldown
            self.last_released_by[left] = log.coder
            self.last_released_by[right] = log.coder
