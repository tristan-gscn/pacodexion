from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationResult:
    status: str  # "OK", "WARN", "KO"
    detail: str = ""
    warnings: List[str] = field(default_factory=list)

    @property
    def is_ok(self) -> bool:
        return self.status in ("OK", "WARN")

    @property
    def is_warn(self) -> bool:
        return self.status == "WARN"

    @property
    def is_ko(self) -> bool:
        return self.status == "KO"
