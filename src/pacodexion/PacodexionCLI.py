from __future__ import annotations

import argparse
import os
import subprocess
import sys
from typing import List, Sequence

from .CaseRegistry import CaseRegistry
from .CaseRunner import CaseRunner
from .KoTraceWriter import KoTraceWriter
from .ResultFormatter import ResultFormatter
from .TestCase import TestCase


class PacodexionCLI:
    def __init__(self) -> None:
        self.registry = CaseRegistry()
        self.runner = CaseRunner()
        self.trace_writer = KoTraceWriter()
        self.use_color = sys.stdout.isatty()
        self.formatter = ResultFormatter(use_color=self.use_color)

    def parse_args(self, argv: Sequence[str]) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog="pacodexion",
            description="Run Codexion scenarios against ./codexion and validate logs.",
        )
        parser.add_argument(
            "cases",
            nargs="*",
            help="Case keys to run (example: 1 big error_arg3). If omitted, run all.",
        )
        parser.add_argument(
            "--binary",
            default="./codexion",
            help="Path to codexion binary (default: ./codexion).",
        )
        parser.add_argument(
            "--timeout",
            type=float,
            default=60.0,
            help="Per-test timeout in seconds (default: 60).",
        )
        parser.add_argument(
            "-a",
            "--all-traces",
            action="store_true",
            help="Write traces for all cases in traces/ok and traces/ko.",
        )
        parser.add_argument(
            "-r",
            "--raw",
            action="store_true",
            help="Print raw codexion output only (without OK/KO rendering).",
        )
        parser.add_argument(
            "-c",
            "--copy",
            action="store_true",
            help="Copy raw output to clipboard (requires -r and exactly one case).",
        )
        return parser.parse_args(argv)

    def run(self, argv: Sequence[str]) -> int:
        args = self.parse_args(argv)
        selected, unknown = self.registry.select_cases(args.cases)

        if unknown:
            for token in unknown:
                print(f"[FAIL] unknown test key: {token}", file=sys.stderr)
            return 2

        if not os.path.exists(args.binary):
            print(f"[FAIL] binary not found: {args.binary}", file=sys.stderr)
            return 2
        if not os.access(args.binary, os.X_OK):
            print(f"[FAIL] binary is not executable: {args.binary}", file=sys.stderr)
            return 2

        if args.copy and not args.raw:
            print("[FAIL] --copy requires --raw", file=sys.stderr)
            return 2
        if args.copy and len(selected) != 1:
            print(
                "[FAIL] --copy requires exactly one test key in arguments",
                file=sys.stderr,
            )
            return 2
        if args.raw:
            return self._run_cases_raw(
                args.binary,
                selected,
                args.timeout,
                copy_to_clipboard=args.copy,
            )

        results = self._run_cases_live(
            args.binary,
            selected,
            args.timeout,
            all_traces=args.all_traces,
        )
        any_fail = any(not ok for _, ok, _ in results)
        print(self.formatter.render_summary(results))
        return 1 if any_fail else 0

    def _run_cases_live(
        self,
        binary: str,
        selected: List[TestCase],
        timeout: float,
        *,
        all_traces: bool,
    ) -> List[tuple[TestCase, bool, str]]:
        results: List[tuple[TestCase, bool, str]] = []
        spinner_frames = ["|", "/", "-", "\\"]

        for case in selected:
            spinner_index = 0
            started_line = False

            def on_tick(_: float) -> None:
                nonlocal spinner_index, started_line
                if not sys.stdout.isatty():
                    if not started_line:
                        print(self.formatter.render_running(case, spinner_frames[0]))
                        started_line = True
                    return
                frame = spinner_frames[spinner_index % len(spinner_frames)]
                spinner_index += 1
                print(self.formatter.render_running(case, frame), end="", flush=True)
                started_line = True

            ok, detail = self.runner.run_case_with_progress(binary, case, timeout, on_tick=on_tick)
            if started_line and sys.stdout.isatty():
                print("\r" + " " * 100 + "\r", end="")
            print(self.formatter.render_result(case, ok, detail))
            if all_traces or not ok:
                subdir = ("ok" if ok else "ko") if all_traces else None
                trace_file = self.trace_writer.write(
                    case,
                    self.runner.get_last_output(),
                    detail,
                    subdir=subdir,
                    highlight_failure=not ok,
                )
                print(f"  trace: {trace_file}")
            results.append((case, ok, detail))

        return results

    def _run_cases_raw(
        self,
        binary: str,
        selected: List[TestCase],
        timeout: float,
        *,
        copy_to_clipboard: bool,
    ) -> int:
        raw_outputs: List[str] = []
        several_cases = len(selected) > 1

        for index, case in enumerate(selected):
            self.runner.run_case_with_progress(binary, case, timeout, on_tick=None)
            raw_output = self.runner.get_last_output()
            raw_outputs.append(raw_output)

            if several_cases:
                print(f"=== {case.key} ({case.name}) ===")
            if raw_output:
                print(raw_output, end="" if raw_output.endswith("\n") else "\n")
            if several_cases and index < len(selected) - 1:
                print()

        if copy_to_clipboard:
            copy_error = self._copy_to_clipboard(raw_outputs[0])
            if copy_error is not None:
                print(f"[FAIL] {copy_error}", file=sys.stderr)
                return 2
            print(self._blue("\nLog copied to clipboard."))

        return 0

    def _blue(self, text: str) -> str:
        if not self.use_color:
            return text
        return f"\033[34m{text}\033[0m"

    def _copy_to_clipboard(self, text: str) -> str | None:
        clipboard_commands = [
            ["wl-copy"],
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
            ["pbcopy"],
            ["clip.exe"],
        ]
        for command in clipboard_commands:
            try:
                subprocess.run(
                    command,
                    input=text,
                    text=True,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    timeout=1,
                )
                return None
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                # Some clipboard tools keep a helper process alive after data is
                # transferred; treat timeout as copied to avoid false failures.
                return None
            except subprocess.CalledProcessError as exc:
                stderr = (exc.stderr or "").strip()
                if stderr:
                    return f"clipboard copy failed with {command[0]}: {stderr}"
                return f"clipboard copy failed with {command[0]}"
        tried = ", ".join(command[0] for command in clipboard_commands)
        return f"no clipboard utility found ({tried})"
