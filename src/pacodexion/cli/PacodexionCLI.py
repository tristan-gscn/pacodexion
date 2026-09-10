import argparse
import os
import sys
from typing import Sequence
from ..cases.CaseRegistry import CaseRegistry
from ..formatter.ResultFormatter import ResultFormatter
from ..runner.CaseRunner import CaseRunner
from ..traces.TraceWriter import TraceWriter
from .CliParser import CliParser
from .LiveRunner import LiveRunner


class PacodexionCLI:
    DEFAULT_TIMEOUT: float = 15.0

    def __init__(self) -> None:
        self.parser = CliParser()
        self.registry = CaseRegistry()
        self.runner = CaseRunner()
        self.trace_writer = TraceWriter()
        self.formatter = ResultFormatter(use_color=sys.stdout.isatty())
        self.live_runner = LiveRunner(self.runner, self.formatter, self.trace_writer)

    def parse_args(self, argv: Sequence[str]) -> argparse.Namespace:
        return self.parser.parse(argv)

    def run(self, argv: Sequence[str]) -> int:
        args = self.parser.parse(argv)

        if args.list:
            print(self.formatter.render_cases_list(self.registry.all_cases()))
            return 0

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

        results = self.live_runner.run_suite(
            args.binary,
            selected,
            self.DEFAULT_TIMEOUT,
            save_traces=args.save_traces,
        )
        print(self.formatter.render_summary(results))
        return 1 if any(res.is_ko for _, res in results) else 0
