from __future__ import annotations

from typing import Any

from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from .safety import require_action
from .skills import Skill, Step


def _render(value: Any, params: dict[str, str]) -> Any:
    if isinstance(value, str):
        result = value
        for key, replacement in params.items():
            result = result.replace("{{" + key + "}}", replacement)
        return result
    if isinstance(value, list):
        return [_render(item, params) for item in value]
    if isinstance(value, dict):
        return {key: _render(item, params) for key, item in value.items()}
    return value


def _semantic_locator(page: Page, candidates: list[dict[str, Any]]) -> Locator:
    """Return the first visible semantic locator from ordered fallbacks."""
    for candidate in candidates:
        if "role" in candidate:
            locator = page.get_by_role(candidate["role"], name=candidate.get("name"))
        elif "placeholder" in candidate:
            locator = page.get_by_placeholder(candidate["placeholder"])
        elif "text" in candidate:
            locator = page.get_by_text(candidate["text"], exact=candidate.get("exact", True))
        else:
            continue

        try:
            locator.first.wait_for(state="visible", timeout=1500)
            return locator.first
        except PlaywrightTimeoutError:
            continue

    raise LookupError(f"No semantic locator matched candidates: {candidates!r}")


class BrowserExecutor:
    def __init__(self, *, headless: bool = False) -> None:
        self.headless = headless

    def execute(self, skill: Skill, params: dict[str, str], *, approved: bool = False) -> None:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=self.headless)
            page = browser.new_page()
            try:
                for step in skill.steps:
                    self._run_step(page, step, params, approved=approved)
            finally:
                browser.close()

    def _run_step(
        self,
        page: Page,
        step: Step,
        params: dict[str, str],
        *,
        approved: bool,
    ) -> None:
        args = _render(step.args, params)
        if step.risk != "safe":
            require_action(step.risk, approved=approved)

        match step.action:
            case "goto":
                page.goto(args["url"], wait_until="domcontentloaded")
            case "fill_role":
                page.get_by_role(args["role"], name=args.get("name")).fill(args["value"])
            case "click_role":
                page.get_by_role(args["role"], name=args.get("name")).click()
            case "press_role":
                page.get_by_role(args["role"], name=args.get("name")).press(args["key"])
            case "fill_placeholder":
                page.get_by_placeholder(args["placeholder"]).fill(args["value"])
            case "click_text":
                page.get_by_text(args["text"], exact=args.get("exact", True)).click()
            case "fill_semantic":
                _semantic_locator(page, args["candidates"]).fill(args["value"])
            case "press_semantic":
                _semantic_locator(page, args["candidates"]).press(args["key"])
            case "click_semantic":
                _semantic_locator(page, args["candidates"]).click()
            case "wait_for_url":
                page.wait_for_url(args["url"])
            case "wait":
                page.wait_for_timeout(int(args["ms"]))
            case _:
                raise ValueError(f"Unsupported browser action: {step.action}")
