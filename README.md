# retainbook

A local-first session notebook for coding agents. Record decisions and open
loops, search them later, and print a short brief the next session can
load. Nothing leaves your machine. No model and no API key are required.

A longer `CLAUDE.md` still cannot remember "we tried this in March and it
broke prod." retainbook is the small notebook for that.

## Install

Python 3.10 or later.

From a checkout:

```bash
python3 -m pip install .
python3 -m pip install -e ".[dev]"  # optional, for tests
retainbook --db ./retainbook.db add "Auth timeout" "Tried JWT refresh in March and it broke prod." --kind decision
```

## 30-second quick start

```bash
retainbook --db ./retainbook.db add "Auth timeout" "Tried JWT refresh in March and it broke prod." --kind decision --tags auth
retainbook --db ./retainbook.db add "Customer waiting" "Acme is still waiting on the timeout fix." --kind open --tags acme
retainbook --db ./retainbook.db recall timeout
retainbook --db ./retainbook.db brief
```

Sample output from that exact example:

```
$ retainbook --db ./retainbook.db add "Auth timeout" "Tried JWT refresh in March and it broke prod." --kind decision --tags auth
added #1
$ retainbook --db ./retainbook.db add "Customer waiting" "Acme is still waiting on the timeout fix." --kind open --tags acme
added #2

$ retainbook --db ./retainbook.db recall timeout
#2 2026-11-09T21:40:16Z [open] tags=acme Customer waiting
Acme is still waiting on the timeout fix.
---
#1 2026-11-09T21:40:16Z [decision] tags=auth Auth timeout
Tried JWT refresh in March and it broke prod.
---
$ retainbook --db ./retainbook.db brief
# retainbook brief

## Decisions
- (1) Auth timeout [auth] — Tried JWT refresh in March and it broke prod.

## Open loops
- (2) Customer waiting [acme] — Acme is still waiting on the timeout fix.
```

Timestamps are UTC and will differ on your machine. The ids, kinds, tags, and bodies should match if you use the same commands.

`--db` is optional; the default file is `~/.retainbook/retainbook.db`.

## Credit

Motivated by the surge of interest in persistent session memory for coding
agents, and by the complaint that agents can read a repo but not the
human context around it. Original SQLite CLI; no source was copied from
any memory product.

## Limits

- Notes live in a local SQLite file (default `~/.retainbook/retainbook.db`). Nothing is sent over the network.
- Search uses FTS5 when the query is a valid MATCH, and falls back to LIKE otherwise.
- `--limit` must be a positive integer.
- Do not store secrets in notes if the database file might be shared or backed up unsafely.

From GitHub you can also install with:

```bash
python3 -m pip install git+https://github.com/perron/retainbook.git
```

This package is not published to PyPI.

## Use it with your agent

You can point a coding agent at this repository and ask it to use the tool, adapt it, or write a small tool in the same style. That works with Claude Code, Codex, Cursor, Grok Bot, and anything else that can clone a git repo and run a Python CLI.

A short prompt you can paste:

> Clone https://github.com/perron/retainbook, install it, and record this decision in a local ./retainbook.db: we are keeping retainbook as a local-first notebook with no API key. Then print a brief.

If you want a new tool in this style, say so explicitly: one job, standard-library Python, pytest first, no API key, and an honest Limits section.

## Contributing / how you can help

Bug reports, tight tests, and small honest features are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to run the suite and for pull request guidelines.

Good first issues:

- Add `edit` and `delete` commands that address a note by id, with tests.
- Export and import a markdown folder so a notebook can be reviewed in git.
- Let `brief` filter by tag.

If you are unsure whether an idea fits, open an issue before writing a large patch.

## License

MIT. See `LICENSE`. Please read `SECURITY.md` before filing a vulnerability report. Agents should also read `AGENTS.md`.
