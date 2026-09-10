from __future__ import annotations

import subprocess
from pacodexion.cases.TestCase import TestCase
from pacodexion.validator.OutputValidator import OutputValidator


def make_completed(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["./codexion"],
        returncode=returncode,
        stdout=stdout,
        stderr="",
    )


def test_burnout_latency_ok() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "100", "50", "50", "50", "1", "10", "fifo"), expect_burnout=True)
    # Burnout exactly at 105ms (5ms lateness <= 10ms target) -> OK
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "105 2 burned out\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "OK"
    assert not result.warnings


def test_burnout_latency_warn() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "100", "50", "50", "50", "1", "10", "fifo"), expect_burnout=True)
    # Burnout at 115ms (15ms lateness: >10ms and <=25ms) -> WARN
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "115 2 burned out\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "WARN"
    assert result.is_warn
    assert len(result.warnings) == 1
    assert "tolerance <=25ms" in result.warnings[0]


def test_burnout_latency_ko() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "100", "50", "50", "50", "1", "10", "fifo"), expect_burnout=True)
    # Burnout at 130ms (30ms lateness > 25ms) -> KO
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "130 2 burned out\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "KO"
    assert result.is_ko
    assert "burnout detection delayed beyond 25ms tolerance" in result.detail


def test_adjacent_coders_cannot_compile_simultaneously() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("4", "500", "100", "100", "100", "1", "10", "fifo"))
    # Coder 1 and coder 2 (adjacent neighbors) both compiling simultaneously at ts 10
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "1 2 has taken a dongle\n"
        "1 2 has taken a dongle\n"
        "1 2 is compiling\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "KO"
    assert "two adjacent coders compiling simultaneously" in result.detail


def test_dongle_cooldown_enforcement() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "1000", "50", "10", "10", "2", "50", "fifo"))
    # Coder 1 finishes compiling at ts 50 (dongles cooldown until 50+50=100)
    # Coder 2 acquires dongles and tries to compile at ts 70 (<100) -> KO cooldown violation
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "50 1 is debugging\n"
        "55 2 has taken a dongle\n"
        "60 2 has taken a dongle\n"
        "70 2 is compiling\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "KO"
    assert "cooldown violation" in result.detail


def test_dongle_cooldown_jitter_warn() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "1000", "50", "10", "10", "1", "50", "fifo"))
    # Coder 1 finishes compiling at ts 50 (dongles cooldown until 50+50=100)
    # Coder 2 compiles at ts 97 (only 3ms before 100ms, <= 10ms tolerance) -> WARN
    logs = (
        "0 1 has taken a dongle\n"
        "0 1 has taken a dongle\n"
        "0 1 is compiling\n"
        "50 1 is debugging\n"
        "90 2 has taken a dongle\n"
        "95 2 has taken a dongle\n"
        "97 2 is compiling\n"
        "147 2 is debugging\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "WARN"
    assert result.is_warn
    assert any("before cooldown expiration" in w for w in result.warnings)


def test_non_monotonic_timestamp_warn_only_when_coherent() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "1000", "10", "5", "5", "1", "0", "fifo"))
    logs = (
        "0 1 has taken a dongle\n"
        "1 1 has taken a dongle\n"
        "2 1 is compiling\n"
        "12 1 is debugging\n"
        "17 1 is refactoring\n"
        "30 2 has taken a dongle\n"
        "29 2 has taken a dongle\n"
        "31 2 is compiling\n"
        "41 2 is debugging\n"
        "46 2 is refactoring\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "WARN"
    assert any("non-monotonic timestamp in printed logs" in w for w in result.warnings)


def test_compile_without_two_takes_is_invalid() -> None:
    validator = OutputValidator()
    case = TestCase("t", "test", ("2", "1000", "10", "5", "5", "1", "0", "fifo"))
    logs = (
        "0 1 has taken a dongle\n"
        "1 1 is compiling\n"
    )
    result = validator.validate_regular_case(make_completed(logs), case)
    assert result.status == "KO"
    assert "invalid state transition sequence" in result.detail
