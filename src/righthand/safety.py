from __future__ import annotations

from dataclasses import dataclass


IRREVERSIBLE_ACTIONS = {
    "publish",
    "delete",
    "pay",
    "purchase",
    "send",
    "submit",
    "confirm_order",
}


class ApprovalRequired(RuntimeError):
    """Raised when a skill needs explicit human approval."""


@dataclass(frozen=True)
class SafetyDecision:
    allowed: bool
    reason: str


def check_action(action: str, *, approved: bool = False) -> SafetyDecision:
    normalized = action.strip().lower()
    if normalized in IRREVERSIBLE_ACTIONS and not approved:
        return SafetyDecision(False, f"'{normalized}' requires explicit human approval")
    return SafetyDecision(True, "allowed")


def require_action(action: str, *, approved: bool = False) -> None:
    decision = check_action(action, approved=approved)
    if not decision.allowed:
        raise ApprovalRequired(decision.reason)
