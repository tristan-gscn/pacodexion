from __future__ import annotations


class AnsiStyler:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"

    def __init__(self, use_color: bool = True) -> None:
        self.use_color = use_color

    def color(self, text: str, code: str) -> str:
        if not self.use_color:
            return text
        return f"{code}{text}{self.RESET}"

    def bold(self, text: str) -> str:
        if not self.use_color:
            return text
        return f"{self.BOLD}{text}{self.RESET}"
