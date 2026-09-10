from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedLog:
    line_no: int
    ts: int
    coder: int
    state: str
    raw: str
