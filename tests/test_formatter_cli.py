from __future__ import annotations

import pytest
from pacodexion.cases.TestCase import TestCase
from pacodexion.cli.PacodexionCLI import PacodexionCLI
from pacodexion.formatter.ResultFormatter import ResultFormatter
from pacodexion.validator.ValidationResult import ValidationResult


def test_formatter_ok() -> None:
    formatter = ResultFormatter(use_color=False)
    case = TestCase("1", "test_ok", ())
    rendered = formatter.render_result(case, ValidationResult(status="OK"))
    assert "[OK] 1 (test_ok)" in rendered


def test_formatter_warn() -> None:
    formatter = ResultFormatter(use_color=False)
    case = TestCase("2", "test_warn", ())
    res = ValidationResult(status="WARN", warnings=["warning: burnout delayed by 18ms"])
    rendered = formatter.render_result(case, res)
    assert "[WARN] 2 (test_warn)" in rendered
    assert "warning: burnout delayed by 18ms" in rendered


def test_formatter_ko() -> None:
    formatter = ResultFormatter(use_color=False)
    case = TestCase("3", "test_ko", ())
    res = ValidationResult(status="KO", detail="burnout delayed beyond 25ms")
    rendered = formatter.render_result(case, res)
    assert "[KO] 3 (test_ko)" in rendered
    assert "burnout delayed beyond 25ms" in rendered


def test_formatter_summary() -> None:
    formatter = ResultFormatter(use_color=False)
    case1 = TestCase("1", "ok", ())
    case2 = TestCase("2", "warn", ())
    results = [
        (case1, ValidationResult(status="OK")),
        (case2, ValidationResult(status="WARN", warnings=["w1"])),
    ]
    summary = formatter.render_summary(results)
    assert "Summary: 2/2 passed (1 with warnings)" in summary


def test_cli_rejects_removed_flags() -> None:
    cli = PacodexionCLI()
    for flag in ["--copy", "-c", "--raw", "-r", "--timeout", "-t", "--all-traces", "-a"]:
        with pytest.raises(SystemExit):
            cli.parse_args([flag])


def test_cli_accepts_binary_and_cases() -> None:
    cli = PacodexionCLI()
    args = cli.parse_args(["--binary", "my_bin", "1", "starvation"])
    assert args.binary == "my_bin"
    assert args.cases == ["1", "starvation"]


def test_cli_list_flag() -> None:
    cli = PacodexionCLI()
    args = cli.parse_args(["--list"])
    assert args.list is True


def test_formatter_cases_list() -> None:
    formatter = ResultFormatter(use_color=False)
    case = TestCase("1", "test_case", ("4", "800", "200"), description="Test description")
    listing = formatter.render_cases_list([case])
    assert "1" in listing
    assert "test_case" in listing
    assert "4 800 200" in listing
    assert "Test description" in listing
