from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class TestCase:
    key: str
    name: str
    args: Tuple[str, ...]
    expect_invalid_args: bool = False
