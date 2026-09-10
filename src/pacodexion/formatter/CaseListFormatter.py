from __future__ import annotations

from typing import Iterable
from ..cases.TestCase import TestCase
from .AnsiStyler import AnsiStyler


class CaseListFormatter:
    def __init__(self, styler: AnsiStyler) -> None:
        self.styler = styler

    def render(self, cases: Iterable[TestCase]) -> str:
        lines: list[str] = [self.styler.bold("Available Codexion test cases:"), ""]
        for case in cases:
            args_str = " ".join(case.args) if case.args else "<none>"
            key_str = self.styler.bold(f"{case.key:<22}")
            name_str = f"({case.name})"
            lines.append(f"  {key_str} {name_str:<22} args: {args_str}")
            if case.description:
                lines.append(f"    {'':<22} {self.styler.color(case.description, self.styler.CYAN)}")
        return "\n".join(lines)
