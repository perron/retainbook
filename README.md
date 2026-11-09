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

## 30-second example

```bash
retainbook --db ./retainbook.db add "Auth timeout" "Tried JWT refresh in March and it broke prod." --kind decision --tags auth
retainbook --db ./retainbook.db add "Customer waiting" "Acme is still waiting on the timeout fix." --kind open --tags acme
retainbook --db ./retainbook.db recall timeout
retainbook --db ./retainbook.db brief
```

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

## License

MIT. See `LICENSE`. Please read `SECURITY.md` before filing a vulnerability report.
