from __future__ import annotations

from typing import List, Tuple
from ..cases.TestCase import TestCase
from .ActionDurationTracker import ActionDurationTracker
from .BurnoutTracker import BurnoutTracker
from .DongleTracker import DongleTracker
from .OutcomeEvaluator import OutcomeEvaluator
from .ParsedLog import ParsedLog
from .StateSequenceTracker import StateSequenceTracker
from .ValidationResult import ValidationResult


class SimulationValidator:
    def __init__(self) -> None:
        self.evaluator = OutcomeEvaluator()

    def simulate(
        self,
        case: TestCase,
        logs: List[ParsedLog],
        params: Tuple[int, int, int, int, int, int, int],
    ) -> ValidationResult:
        n, t_burn, t_comp, t_dbg, t_ref, n_comp, cd = params
        seq = StateSequenceTracker(n)
        dongles = DongleTracker(n, cd)
        actions = ActionDurationTracker(t_comp, t_dbg, t_ref, n)
        burn = BurnoutTracker(t_burn)
        warnings: List[str] = []

        for idx, log in enumerate(logs):
            err, warns = self._dispatch(log, seq, dongles, actions, burn, idx, logs)
            warnings.extend(warns)
            if err:
                return err

        return self.evaluator.evaluate(case, burn, actions, n_comp, warnings)

    def _dispatch(
        self,
        log: ParsedLog,
        seq: StateSequenceTracker,
        dongles: DongleTracker,
        actions: ActionDurationTracker,
        burn: BurnoutTracker,
        idx: int,
        logs: List[ParsedLog],
    ) -> Tuple[ValidationResult | None, List[str]]:
        t_err = seq.check_transition(log)
        if t_err:
            return t_err, []
        if log.state == "has taken a dongle":
            return actions.on_taken_dongle(log), []
        if log.state == "is compiling":
            c_err, c_warn = dongles.on_compiling(log)
            if not c_err:
                actions.on_compiling(log)
            return c_err, c_warn
        if log.state == "is debugging":
            dongles.on_debugging(log)
            return actions.on_debugging(log)
        if log.state == "is refactoring":
            return actions.on_refactoring(log)
        if log.state == "burned out":
            dongles.compiling_coders.discard(log.coder)
            return burn.on_burnout(log, actions.last_compile[log.coder], idx + 1, logs)
        return None, []
