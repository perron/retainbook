# retainbook proof

Captured 2026-11-09 13:27 PST.

Fresh-venv install: `pip install .` succeeded and `retainbook --version` printed `retainbook 0.1.1`.

Tests: 12 passed in 0.08s

```
added #1
added #2

# recall timeout
#2 2026-11-09T21:27:00Z [open] tags=acme Customer waiting
Acme is still waiting on the timeout fix.
---
#1 2026-11-09T21:27:00Z [decision] tags=auth Auth timeout
Tried JWT refresh in March and it broke prod.
---
# brief
# retainbook brief

## Decisions
- (1) Auth timeout [auth] — Tried JWT refresh in March and it broke prod.

## Open loops
- (2) Customer waiting [acme] — Acme is still waiting on the timeout fix.
```
