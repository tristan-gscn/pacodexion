from __future__ import annotations

import re
from typing import List, Optional, Tuple
from .ParsedLog import ParsedLog
from .ValidationResult import ValidationResult


class LogParser:
    LOG_RE = re.compile(
        r"^(?P<ts>\d+)\s+(?P<coder>\d+)\s+"
        r"(?P<state>has taken a dongle|is compiling|is debugging|is refactoring|burned out)$"
    )

    def parse_lines(
        self, raw_lines: List[str], n_coders: int
    ) -> Tuple[Optional[List[ParsedLog]], Optional[ValidationResult], List[str]]:
        parsed: List[ParsedLog] = []
        warnings: List[str] = []
        last_ts = -1

        for idx, line in enumerate(raw_lines, start=1):
            match = self.LOG_RE.match(line)
            if not match:
                return None, ValidationResult(
                    status="KO",
                    detail=(
                        "invalid log format\n"
                        f"line={idx}\n"
                        f"value={line}\n"
                        "expected_format='<timestamp_ms> <coder_id> <state>'\n"
                        "allowed_states=['has taken a dongle', 'is compiling', "
                        "'is debugging', 'is refactoring', 'burned out']"
                    ),
                ), []
            ts = int(match.group("ts"))
            coder = int(match.group("coder"))
            state = match.group("state")

            if ts < last_ts:
                warnings.append(
                    "non-monotonic timestamp in printed logs\n"
                    f"line={idx}\n"
                    f"previous_timestamp={last_ts}\n"
                    f"current_timestamp={ts}\n"
                    f"line_value={line}"
                )
            last_ts = ts

            if coder < 1 or coder > n_coders:
                return None, ValidationResult(
                    status="KO",
                    detail=(
                        "coder id out of expected range\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"expected_range=1..{n_coders}\n"
                        f"line_value={line}"
                    ),
                ), []
            parsed.append(ParsedLog(line_no=idx, ts=ts, coder=coder, state=state, raw=line))
        return parsed, None, warnings
