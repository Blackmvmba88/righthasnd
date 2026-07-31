from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any


@dataclass(frozen=True)
class Step:
    action: str
    args: dict[str, Any]
    risk: str = "safe"


@dataclass(frozen=True)
class Skill:
    name: str
    aliases: tuple[str, ...]
    description: str
    match: str
    steps: tuple[Step, ...]

    def parse(self, utterance: str) -> dict[str, str] | None:
        found = re.search(self.match, utterance, flags=re.IGNORECASE)
        return found.groupdict() if found else None


class SkillRegistry:
    def __init__(self, skills: list[Skill] | None = None) -> None:
        self._skills = skills or []

    @classmethod
    def from_directory(cls, directory: Path) -> "SkillRegistry":
        loaded: list[Skill] = []
        for path in sorted(directory.glob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            loaded.append(
                Skill(
                    name=data["name"],
                    aliases=tuple(data.get("aliases", [])),
                    description=data.get("description", ""),
                    match=data["match"],
                    steps=tuple(
                        Step(
                            action=step["action"],
                            args=step.get("args", {}),
                            risk=step.get("risk", "safe"),
                        )
                        for step in data["steps"]
                    ),
                )
            )
        return cls(loaded)

    def resolve(self, utterance: str) -> tuple[Skill, dict[str, str]]:
        normalized = utterance.strip()
        for skill in self._skills:
            parsed = skill.parse(normalized)
            if parsed is not None:
                return skill, parsed
        raise LookupError(f"No skill matches: {utterance!r}")

    def names(self) -> list[str]:
        return [skill.name for skill in self._skills]


def builtin_registry() -> SkillRegistry:
    directory = Path(__file__).with_name("builtin_skills")
    return SkillRegistry.from_directory(directory)
