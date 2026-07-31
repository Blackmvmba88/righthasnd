# RightHand

BlackMamba semantic computer-control assistant.

RightHand turns short spoken or typed intents into reusable browser actions. The design goal is to remove repetitive mouse/keyboard work while keeping irreversible actions behind explicit human approval.

## Core idea

```text
voice / text
    ↓
semantic intent resolver
    ↓
trusted skill registry
    ↓
browser executor
    ↓
safety gate
    ↓
result / human approval
```

The MVP intentionally avoids coordinate macros such as `click(812, 443)`. Skills target semantic UI properties such as roles, accessible names, placeholders, and visible text, with ordered fallbacks when a site changes labels or language.

## Install

Requires Python 3.11+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
playwright install chromium
```

## Use

List installed skills:

```bash
righthand skills
```

Run the first built-in skill:

```bash
righthand run "busca en pinterest western rosa cinematografica"
```

The current Pinterest skill understands forms such as:

```text
busca en pinterest <consulta>
pinterest busca <consulta>
search pinterest <query>
```

## Teach RightHand a browser flow

RightHand uses Playwright's recorder as raw demonstration capture:

```bash
righthand learn pinterest.visual_search https://www.pinterest.com/
```

Perform the flow once in the browser and close the recorder when finished. The demonstration is saved under `recordings/`.

A recording is **not automatically trusted or replayed**. It is training evidence that should be converted into a semantic skill definition first. This prevents a captured accidental click from silently becoming permanent automation.

## Safety contract

Safe navigation and form-preparation steps may execute directly.

Irreversible operations require explicit approval. Current protected action classes include:

- publish
- delete
- pay / purchase
- send
- submit
- confirm_order

An executor step declares its risk. A protected step fails closed unless the caller explicitly passes approval.

## Repository layout

```text
src/righthand/
├── browser.py          # Playwright semantic executor
├── cli.py              # command-line interface
├── recorder.py         # demonstration capture
├── safety.py           # human approval gate
├── skills.py           # semantic registry + resolver
└── builtin_skills/
    └── pinterest.search.json

tests/
├── test_safety.py
└── test_skills.py
```

## Next milestone

The next useful layer is `RightHand Observer`: convert Playwright recordings into candidate semantic skills, show the proposed mapping (`"this means visual search"`), and require one human confirmation before promoting the candidate into the trusted registry.
