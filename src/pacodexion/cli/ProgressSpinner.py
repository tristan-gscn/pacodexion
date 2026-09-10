from __future__ import annotations

import sys


class ProgressSpinner:
    FRAMES = ("|", "/", "-", "\\")

    def __init__(self) -> None:
        self.index = 0

    def next_frame(self) -> str:
        frame = self.FRAMES[self.index % len(self.FRAMES)]
        self.index += 1
        return frame

    def clear(self) -> None:
        if sys.stdout.isatty():
            print("\r" + " " * 100 + "\r", end="")
