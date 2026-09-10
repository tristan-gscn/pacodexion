from __future__ import annotations

from typing import List, Optional, Tuple


class CaseArgsParser:
    @staticmethod
    def is_integer(value: str) -> bool:
        if not value:
            return False
        if value[0] in "+-":
            return value[1:].isdigit()
        return value.isdigit()

    def parse(
        self, raw_args: Tuple[str, ...]
    ) -> Tuple[Optional[Tuple[int, int, int, int, int, int, int, str]], Optional[str]]:
        if len(raw_args) != 8:
            return None, f"invalid test case definition: expected 8 args, got {len(raw_args)}"

        values = list(raw_args[:7])
        parsed: List[int] = []
        for idx, value in enumerate(values, start=1):
            if not self.is_integer(value):
                return None, f"invalid numeric argument at index {idx}: {value}"
            parsed.append(int(value))

        scheduler = raw_args[7]
        if scheduler not in ("fifo", "edf"):
            return None, f"invalid scheduler in case definition: {scheduler}"

        if parsed[0] <= 0:
            return None, f"number_of_coders must be > 0, got {parsed[0]}"
        if parsed[5] < 0:
            return None, f"number_of_compiles_required must be >= 0, got {parsed[5]}"
        for idx, num in enumerate(parsed[1:], start=2):
            if idx == 6:
                continue
            if num < 0:
                return None, f"time/cooldown argument {idx} must be >= 0, got {num}"

        return (
            (parsed[0], parsed[1], parsed[2], parsed[3], parsed[4], parsed[5], parsed[6], scheduler),
            None,
        )
