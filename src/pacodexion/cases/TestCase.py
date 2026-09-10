from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class TestCase:
    __test__ = False

    key: str
    name: str
    args: Tuple[str, ...]
    description: str = ""
    expect_invalid_args: bool = False
    expect_no_burnout: bool = False
    expect_burnout: bool = False
