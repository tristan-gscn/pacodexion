from __future__ import annotations

import argparse
from typing import Sequence


class CliParser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            prog="pacodexion",
            description="Automated tester and concurrency validator for 42 Codexion.",
        )
        self._setup()

    def _setup(self) -> None:
        self.parser.add_argument(
            "cases",
            nargs="*",
            help="Case keys to run (e.g. 1 starvation tight_timings). If omitted, run all.",
        )
        self.parser.add_argument(
            "-b",
            "--binary",
            default="./codexion",
            help="Path to codexion binary (default: ./codexion).",
        )
        self.parser.add_argument(
            "-l",
            "--list",
            action="store_true",
            help="List all available test cases with descriptions and exit.",
        )
        self.parser.add_argument(
            "-s",
            "--save-traces",
            action="store_true",
            help="Save failure traces to disk under traces/ (disabled by default).",
        )

    def parse(self, argv: Sequence[str]) -> argparse.Namespace:
        return self.parser.parse_args(argv)
