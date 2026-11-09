"""Local-first session notebook for coding agents."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TEXT NOT NULL,
    kind TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '',
    title TEXT NOT NULL,
    body TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
    title, body, tags, kind, content='notes', content_rowid='id'
);
CREATE TRIGGER IF NOT EXISTS notes_ai AFTER INSERT ON notes BEGIN
    INSERT INTO notes_fts(rowid, title, body, tags, kind)
    VALUES (new.id, new.title, new.body, new.tags, new.kind);
END;
"""


def open_db(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def default_db() -> Path:
    return Path.home() / ".retainbook" / "retainbook.db"


def add_note(conn: sqlite3.Connection, title: str, body: str, kind: str, tags: str) -> int:
    created = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    cur = conn.execute(
        "INSERT INTO notes (created, kind, tags, title, body) VALUES (?, ?, ?, ?, ?)",
        (created, kind, tags, title, body),
    )
    conn.commit()
    return int(cur.lastrowid)


def recent(conn: sqlite3.Connection, limit: int) -> list[sqlite3.Row]:
    return list(conn.execute("SELECT * FROM notes ORDER BY id DESC LIMIT ?", (limit,)))


def recall(conn: sqlite3.Connection, query: str, limit: int) -> list[sqlite3.Row]:
    # FTS first; fall back to LIKE so an empty query or odd tokens still work.
    try:
        rows = list(conn.execute(
            "SELECT notes.* FROM notes JOIN notes_fts ON notes.id = notes_fts.rowid "
            "WHERE notes_fts MATCH ? ORDER BY notes.id DESC LIMIT ?",
            (query, limit),
        ))
        if rows:
            return rows
    except sqlite3.OperationalError:
        pass
    like = f"%{query}%"
    return list(conn.execute(
        "SELECT * FROM notes WHERE title LIKE ? OR body LIKE ? OR tags LIKE ? "
        "ORDER BY id DESC LIMIT ?",
        (like, like, like, limit),
    ))


def brief(conn: sqlite3.Connection, limit: int) -> str:
    rows = list(conn.execute(
        "SELECT * FROM notes ORDER BY id DESC LIMIT ?",
        (limit,),
    ))
    if not rows:
        return "No notes in retainbook yet."
    lines = ["# retainbook brief", ""]
    by_kind: dict[str, list[sqlite3.Row]] = {}
    for row in reversed(rows):
        by_kind.setdefault(row["kind"], []).append(row)
    for kind in ("decision", "open", "note"):
        items = by_kind.get(kind) or []
        if not items:
            continue
        heading = {"decision": "Decisions", "open": "Open loops", "note": "Notes"}[kind]
        lines.append(f"## {heading}")
        for row in items:
            tag = f" [{row['tags']}]" if row["tags"] else ""
            lines.append(f"- ({row['id']}) {row['title']}{tag} — {row['body']}")
        lines.append("")
    leftover = [k for k in by_kind if k not in {"decision", "open", "note"}]
    for kind in leftover:
        lines.append(f"## {kind}")
        for row in by_kind[kind]:
            lines.append(f"- ({row['id']}) {row['title']} — {row['body']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def format_row(row: sqlite3.Row) -> str:
    tags = f" tags={row['tags']}" if row["tags"] else ""
    return f"#{row['id']} {row['created']} [{row['kind']}]{tags} {row['title']}\n{row['body']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="retainbook",
        description="Local-first session notebook for coding agents.",
    )
    parser.add_argument("--db", help="SQLite file (default: ~/.retainbook/retainbook.db)")
    parser.add_argument("--version", action="version", version=f"retainbook {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="add a note")
    p_add.add_argument("title")
    p_add.add_argument("body", nargs="?", default="")
    p_add.add_argument("--kind", default="note", choices=["note", "decision", "open"])
    p_add.add_argument("--tags", default="")

    p_recent = sub.add_parser("recent", help="show recent notes")
    p_recent.add_argument("--limit", type=int, default=10)

    p_recall = sub.add_parser("recall", help="search notes")
    p_recall.add_argument("query")
    p_recall.add_argument("--limit", type=int, default=10)
    p_recall.add_argument("--json", action="store_true")

    p_brief = sub.add_parser("brief", help="print a short next-session brief")
    p_brief.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv)
    db_path = Path(args.db) if args.db else default_db()
    conn = open_db(db_path)
    try:
        if args.cmd == "add":
            note_id = add_note(conn, args.title, args.body, args.kind, args.tags)
            print(f"added #{note_id}")
            return 0
        if args.cmd == "recent":
            rows = recent(conn, args.limit)
            if not rows:
                print("no notes")
                return 0
            for row in rows:
                print(format_row(row))
                print("---")
            return 0
        if args.cmd == "recall":
            rows = recall(conn, args.query, args.limit)
            if args.json:
                print(json.dumps([dict(row) for row in rows], indent=2))
            elif not rows:
                print("no matches")
            else:
                for row in rows:
                    print(format_row(row))
                    print("---")
            return 0 if rows else 1
        if args.cmd == "brief":
            sys.stdout.write(brief(conn, args.limit))
            return 0
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
