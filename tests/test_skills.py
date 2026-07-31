from righthand.skills import builtin_registry


def test_resolves_spanish_pinterest_search() -> None:
    skill, params = builtin_registry().resolve("busca en pinterest western rosa cinematografica")
    assert skill.name == "pinterest.search"
    assert params == {"query": "western rosa cinematografica"}


def test_resolves_pinterest_first_form() -> None:
    skill, params = builtin_registry().resolve("pinterest busca vaquera editorial")
    assert skill.name == "pinterest.search"
    assert params["query"] == "vaquera editorial"


def test_unknown_command_fails_closed() -> None:
    registry = builtin_registry()
    try:
        registry.resolve("haz cualquier cosa")
    except LookupError:
        pass
    else:
        raise AssertionError("Unknown commands must not execute by guessing")
