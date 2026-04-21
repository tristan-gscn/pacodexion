from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Optional, Tuple

from .TestCase import TestCase


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

    def validate_regular_case(
        self,
        completed: subprocess.CompletedProcess[str],
        case: TestCase,
    ) -> Tuple[bool, str]:
        parsed_args, parse_error = self._parse_regular_args(case.args)
        if parse_error is not None or parsed_args is None:
            return False, parse_error or "invalid test case definition"

        (
            n_coders,
            time_to_burnout,
            time_to_compile,
            time_to_debug,
            time_to_refactor,
            compiles_required,
            _dongle_cooldown,
            _scheduler,
        ) = parsed_args

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
            if compiles_required == 0:
                return True, "no log line emitted (accepted for required_compiles=0)"
            return False, "empty output while compiles are required"

        last_ts = -1
        burnouts = 0
        burnout_coder: Optional[int] = None
        taken_counts = self._build_counter(n_coders)
        compile_counts = self._build_counter(n_coders)
        last_compile_start = {coder_id: 0 for coder_id in range(1, n_coders + 1)}
        last_debug_start: Dict[int, Optional[int]] = {coder_id: None for coder_id in range(1, n_coders + 1)}
        last_refactor_start: Dict[int, Optional[int]] = {coder_id: None for coder_id in range(1, n_coders + 1)}
        last_state: Dict[int, str] = {coder_id: "init" for coder_id in range(1, n_coders + 1)}

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

            if self._transition_invalid(last_state[coder], state, taken_counts[coder]):
                return (
                    False,
                    "invalid state transition sequence\n"
                    f"line={idx}\n"
                    f"coder_id={coder}\n"
                    f"previous_state={last_state[coder]}\n"
                    f"current_state={state}\n"
                    f"line_value={self._preview(line)}",
                )

            if state == "has taken a dongle":
                taken_counts[coder] += 1
                if taken_counts[coder] > 2:
                    return (
                        False,
                        "more than 2 dongles taken before compile\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"dongles_seen_before_compile={taken_counts[coder]}\n"
                        f"line_value={self._preview(line)}",
                    )
                refactor_start = last_refactor_start[coder]
                if refactor_start is not None:
                    waited = ts - refactor_start
                    if waited < time_to_refactor:
                        return (
                            False,
                            "refactor phase ended too early before taking dongles\n"
                            f"line={idx}\n"
                            f"coder_id={coder}\n"
                            f"expected_min_refactor_ms={time_to_refactor}\n"
                            f"actual_refactor_ms={waited}\n"
                            f"line_value={self._preview(line)}",
                        )
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
                compile_counts[coder] += 1
                last_compile_start[coder] = ts
                last_debug_start[coder] = None
                last_refactor_start[coder] = None
            elif state == "is debugging":
                elapsed_compile = ts - last_compile_start[coder]
                if elapsed_compile < time_to_compile:
                    return (
                        False,
                        "compile phase ended too early before debugging\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"expected_min_compile_ms={time_to_compile}\n"
                        f"actual_compile_ms={elapsed_compile}\n"
                        f"line_value={self._preview(line)}",
                    )
                last_debug_start[coder] = ts
            elif state == "is refactoring":
                debug_start = last_debug_start[coder]
                if debug_start is None:
                    return (
                        False,
                        "refactoring started without debugging start\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"line_value={self._preview(line)}",
                    )
                elapsed_debug = ts - debug_start
                if elapsed_debug < time_to_debug:
                    return (
                        False,
                        "debug phase ended too early before refactoring\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"expected_min_debug_ms={time_to_debug}\n"
                        f"actual_debug_ms={elapsed_debug}\n"
                        f"line_value={self._preview(line)}",
                    )
                last_refactor_start[coder] = ts
            elif state == "burned out":
                burnouts += 1
                burnout_coder = coder
                deadline = last_compile_start[coder] + time_to_burnout
                lateness = ts - deadline
                if lateness < 0:
                    return (
                        False,
                        "burned out before burnout deadline\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"deadline_ms={deadline}\n"
                        f"actual_burnout_ms={ts}\n"
                        f"line_value={self._preview(line)}",
                    )
                if lateness > 10:
                    return (
                        False,
                        "burnout detection delayed beyond 10ms requirement\n"
                        f"line={idx}\n"
                        f"coder_id={coder}\n"
                        f"deadline_ms={deadline}\n"
                        f"actual_burnout_ms={ts}\n"
                        f"delay_ms={lateness}\n"
                        f"line_value={self._preview(line)}",
                    )
                if idx != len(lines):
                    next_line = lines[idx] if idx < len(lines) else "<none>"
                    return (
                        False,
                        "burned out event is not the last log line\n"
                        f"line={idx}\n"
                        f"burned_out_line={self._preview(line)}\n"
                        f"next_line={self._preview(next_line)}",
                    )

            last_state[coder] = state

        if burnouts > 1:
            return False, f"multiple burned out events detected\ncount={burnouts}"

        if case.expect_no_burnout and burnouts > 0:
            return (
                False,
                "burnout is forbidden for this test case\n"
                f"case_key={case.key}\n"
                f"burnout_coder={burnout_coder}",
            )

        if burnouts == 0:
            if compiles_required > 0:
                not_done = [str(coder_id) for coder_id, count in compile_counts.items() if count < compiles_required]
                if not_done:
                    return (
                        False,
                        "simulation ended before all coders reached required compile count\n"
                        f"required_compiles={compiles_required}\n"
                        f"coders_not_done={','.join(not_done[:20])}"
                        f"{'...' if len(not_done) > 20 else ''}",
                    )
        else:
            if compiles_required > 0 and all(count >= compiles_required for count in compile_counts.values()):
                return (
                    False,
                    "burnout happened even though all coders reached required compile count\n"
                    f"burnout_coder={burnout_coder}",
                )

        return True, "logs are coherent"

    def _build_counter(self, n_coders: int) -> Dict[int, int]:
        return {coder_id: 0 for coder_id in range(1, n_coders + 1)}

    def _preview(self, text: str, max_len: int = 240) -> str:
        cleaned = text.replace("\n", "\\n")
        if len(cleaned) <= max_len:
            return cleaned
        return f"{cleaned[:max_len]}...(truncated)"

    def _parse_regular_args(
        self, raw_args: Tuple[str, ...]
    ) -> Tuple[Optional[Tuple[int, int, int, int, int, int, int, str]], Optional[str]]:
        if len(raw_args) != 8:
            return None, f"invalid test case definition: expected 8 args, got {len(raw_args)}"

        values = list(raw_args[:7])
        parsed: List[int] = []
        for idx, value in enumerate(values, start=1):
            if not self._is_integer(value):
                return (
                    None,
                    "invalid numeric argument in case definition\n"
                    f"arg_index={idx}\n"
                    f"value={self._preview(value)}",
                )
            parsed.append(int(value))

        scheduler = raw_args[7]
        if scheduler not in ("fifo", "edf"):
            return None, f"invalid scheduler in case definition\nvalue={self._preview(scheduler)}"

        if parsed[0] <= 0:
            return None, f"number_of_coders must be > 0\nvalue={parsed[0]}"
        if parsed[5] < 0:
            return None, f"number_of_compiles_required must be >= 0\nvalue={parsed[5]}"
        for idx, numeric_value in enumerate(parsed[1:], start=2):
            if idx == 6:
                continue
            if numeric_value < 0:
                return (
                    None,
                    "time/cooldown arguments must be >= 0\n"
                    f"arg_index={idx}\n"
                    f"value={numeric_value}",
                )

        return (parsed[0], parsed[1], parsed[2], parsed[3], parsed[4], parsed[5], parsed[6], scheduler), None

    def _transition_invalid(self, previous_state: str, current_state: str, taken_count: int) -> bool:
        if current_state == "burned out":
            return False
        if previous_state == "init":
            return current_state != "has taken a dongle"
        if previous_state == "has taken a dongle":
            if current_state == "has taken a dongle":
                return taken_count >= 2
            return current_state != "is compiling"
        if previous_state == "is compiling":
            return current_state != "is debugging"
        if previous_state == "is debugging":
            return current_state != "is refactoring"
        if previous_state == "is refactoring":
            return current_state != "has taken a dongle"
        return False

    def _is_integer(self, value: str) -> bool:
        if not value:
            return False
        if value[0] in "+-":
            return value[1:].isdigit()
        return value.isdigit()
