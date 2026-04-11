from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Tuple


class OutputValidator:
    LOG_RE = re.compile(
        r"^(?P<ts>\d+)\s+(?P<coder>\d+)\s+"
        r"(?P<state>has taken a dongle|is compiling|is debugging|is refactoring|burned out)$"
    )

    def read_lines(self, output: str) -> List[str]:
        return [line.strip() for line in output.splitlines() if line.strip()]

    def validate_error_case(self, completed: subprocess.CompletedProcess[str]) -> Tuple[bool, str]:
        merged = (completed.stdout or "") + "\n" + (completed.stderr or "")
        lines = self.read_lines(merged)
        has_error_word = any(
            ("error" in line.lower()) or ("invalid" in line.lower()) or ("usage" in line.lower())
            for line in lines
        )
        if completed.returncode != 0 or has_error_word:
            return True, "invalid argument rejection detected"
        return (
            False,
            "expected invalid-argument rejection but command looked successful\n"
            f"return_code={completed.returncode}\n"
            f"stdout={self._preview(completed.stdout or '<empty>')}\n"
            f"stderr={self._preview(completed.stderr or '<empty>')}",
        )

    def validate_regular_case(self, completed: subprocess.CompletedProcess[str], n_coders: int) -> Tuple[bool, str]:
        if completed.returncode != 0:
            return (
                False,
                "unexpected non-zero exit code\n"
                f"return_code={completed.returncode}\n"
                f"stdout={self._preview(completed.stdout or '<empty>')}\n"
                f"stderr={self._preview(completed.stderr or '<empty>')}",
            )

        lines = self.read_lines(completed.stdout or "")
        if not lines:
            return True, "no log line emitted (accepted)"

        last_ts = -1
        burnouts = 0
        taken_counts = self._build_taken_counts(n_coders)
        compiled_once = False

        for idx, line in enumerate(lines, start=1):
            match = self.LOG_RE.match(line)
            if not match:
                return (
                    False,
                    "invalid log format\n"
                    f"line={idx}\n"
                    f"value={self._preview(line)}\n"
                    "expected_format='<timestamp_ms> <coder_id> <state>'\n"
                    "allowed_states=['has taken a dongle', 'is compiling', "
                    "'is debugging', 'is refactoring', 'burned out']",
                )

            ts = int(match.group("ts"))
            coder = int(match.group("coder"))
            state = match.group("state")

            if ts < last_ts:
                return (
                    False,
                    "non-monotonic timestamps\n"
                    f"line={idx}\n"
                    f"previous_timestamp={last_ts}\n"
                    f"current_timestamp={ts}\n"
                    f"line_value={self._preview(line)}",
                )
            last_ts = ts

            if coder < 1 or coder > n_coders:
                return (
                    False,
                    "coder id out of expected range\n"
                    f"line={idx}\n"
                    f"coder_id={coder}\n"
                    f"expected_range=1..{n_coders}\n"
                    f"line_value={self._preview(line)}",
                )

            if state == "has taken a dongle":
                taken_counts[coder] += 1
            elif state == "is compiling":
                if taken_counts[coder] < 2:
                    return (
                        False,
                        "compile started without 2 prior dongle acquisitions\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"dongles_seen_before_compile={taken_counts[coder]}\n"
                        f"line_value={self._preview(line)}",
                    )
                taken_counts[coder] = 0
                compiled_once = True
            elif state == "burned out":
                burnouts += 1
                if idx != len(lines):
                    next_line = lines[idx] if idx < len(lines) else "<none>"
                    return (
                        False,
                        "burned out event is not the last log line\n"
                        f"line={idx}\n"
                        f"burned_out_line={self._preview(line)}\n"
                        f"next_line={self._preview(next_line)}",
                    )

        if burnouts > 1:
            return False, f"multiple burned out events detected\ncount={burnouts}"
        if not compiled_once and burnouts == 0:
            return (
                False,
                "no terminal condition reached: no compile and no burned out event\n"
                f"first_lines={self._preview(' | '.join(lines[:3]))}",
            )
        return True, "logs are coherent"

    def _build_taken_counts(self, n_coders: int) -> Dict[int, int]:
        return {coder_id: 0 for coder_id in range(1, n_coders + 1)}

    def _preview(self, text: str, max_len: int = 240) -> str:
        cleaned = text.replace("\n", "\\n")
        if len(cleaned) <= max_len:
            return cleaned
        return f"{cleaned[:max_len]}...(truncated)"
