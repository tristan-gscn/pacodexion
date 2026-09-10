from __future__ import annotations

import sys
from typing import List, Tuple
from ..cases.TestCase import TestCase
from ..formatter.ResultFormatter import ResultFormatter
from ..runner.CaseRunner import CaseRunner
from ..traces.TraceWriter import TraceWriter
from ..validator.ValidationResult import ValidationResult
from .ProgressSpinner import ProgressSpinner


class LiveRunner:
    def __init__(
        self,
        runner: CaseRunner,
        formatter: ResultFormatter,
        trace_writer: TraceWriter,
    ) -> None:
        self.runner = runner
        self.formatter = formatter
        self.trace_writer = trace_writer

    def run_suite(
        self,
        binary: str,
        cases: List[TestCase],
        timeout: float,
        *,
        save_traces: bool = False,
    ) -> List[Tuple[TestCase, ValidationResult]]:
        results: List[Tuple[TestCase, ValidationResult]] = []

        for case in cases:
            spinner = ProgressSpinner()
            started = False

            def on_tick(_: float) -> None:
                nonlocal started
                if not sys.stdout.isatty():
                    if not started:
                        print(self.formatter.render_running(case, "|"))
                        started = True
                    return
                print(self.formatter.render_running(case, spinner.next_frame()), end="", flush=True)
                started = True

            result = self.runner.run_case_with_progress(binary, case, timeout, on_tick=on_tick)
            if started:
                spinner.clear()

            print(self.formatter.render_result(case, result))

            if save_traces and (result.is_ko or result.is_warn):
                sub = "ko" if result.is_ko else "warn"
                path = self.trace_writer.write(
                    case,
                    self.runner.get_last_output(),
                    result.detail,
                    subdir=sub,
                    highlight_failure=result.is_ko,
                    warnings=result.warnings,
                )
                print(f"  trace saved: {path}")

            results.append((case, result))
        return results
