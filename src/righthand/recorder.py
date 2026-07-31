from __future__ import annotations

from pathlib import Path
import re
import subprocess


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", name.strip()).strip("-.")
    if not cleaned:
        raise ValueError("Recording name cannot be empty")
    return cleaned


def record(name: str, url: str, *, output_dir: Path = Path("recordings")) -> Path:
    """Launch Playwright codegen and save the demonstrated browser flow.

    The generated recording is evidence/training material. It is intentionally
    not executed automatically as a trusted RightHand skill until reviewed and
    converted into a semantic skill definition.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{safe_name(name)}.py"
    command = [
        "playwright",
        "codegen",
        "--target",
        "python",
        "-o",
        str(destination),
        url,
    ]
    subprocess.run(command, check=True)
    return destination
