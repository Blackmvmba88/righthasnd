import pytest

from righthand.safety import ApprovalRequired, check_action, require_action


def test_safe_action_allowed_without_approval() -> None:
    assert check_action("navigate").allowed is True


def test_publish_requires_approval() -> None:
    assert check_action("publish").allowed is False
    with pytest.raises(ApprovalRequired):
        require_action("publish")


def test_publish_allowed_after_explicit_approval() -> None:
    require_action("publish", approved=True)
