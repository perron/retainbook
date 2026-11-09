# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Cursor, Grok Bot, and similar) working in this repository.

## What this repo is

`retainbook` is a small Python 3.10+ command-line tool to keep a local-first session notebook for decisions and open loops. It has no required runtime dependencies and no API key. Layout:

- `retainbook/cli.py` — the implementation and the `main()` entry point (exit code is an `int`)
- `retainbook/__main__.py` — `python -m retainbook`
- `retainbook/__init__.py` — `__version__`
- `tests/test_retainbook.py` — pytest suite
- `pyproject.toml` — packaging, the `retainbook` script, and the `dev` extra (`pytest`)
- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `PROOF.md` — human docs

retainbook/cli.py is a SQLite notebook with FTS5 and a LIKE fallback. tests/test_retainbook.py covers add/recall/brief, unicode, and --limit validation.

## How to run tests

```bash
python3 -m pip install -e ".[dev]"
python3 -m pytest -q
retainbook --help
retainbook --version
```

`pip install .` in a fresh virtualenv must leave `retainbook` on `PATH`.

## Conventions

- Keep changes small. Match the existing style: standard library, type hints, `argparse`, exit codes documented in the README.
- If you add behavior, add a test for it. Prefer tests of user-visible behavior over tests of internals.
- Do not add network calls, API keys, or telemetry.
- Do not copy source from other tools. This is a clean-room project.
- If a README, SECURITY.md, or Limits section would become untrue, update it in the same change.
- Do not commit secrets. For `retainbook`, also do not commit local store/journal/database files (see `.gitignore`).
- Token estimates in this family of tools, when present, are `ceil(utf-8 bytes / 4)`. Do not describe them as a vendor tokenizer.

## If you are using the tool rather than changing it

Install it from this checkout or from `pip install git+https://github.com/perron/retainbook.git`, then follow the 30-second quick start in the README. The README Limits section is the contract for what this release does and does not do.
