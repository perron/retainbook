from pathlib import Path
import json
import pytest
import retainbook.cli as rb


def test_help_and_version():
    with pytest.raises(SystemExit) as exc:
        rb.main(["--help"])
    assert exc.value.code == 0
    with pytest.raises(SystemExit) as exc:
        rb.main(["--version"])
    assert exc.value.code == 0


def test_add_recall_brief(tmp_path, capsys):
    db = tmp_path / "notes.db"
    assert rb.main(["--db", str(db), "add", "Auth timeout", "Tried JWT refresh in March and it broke prod.", "--kind", "decision", "--tags", "auth"]) == 0
    assert rb.main(["--db", str(db), "add", "Customer waiting", "Acme is still waiting on the timeout fix.", "--kind", "open", "--tags", "acme"]) == 0
    assert rb.main(["--db", str(db), "recall", "timeout"]) == 0
    out = capsys.readouterr().out
    assert "Auth timeout" in out
    assert "Customer waiting" in out
    assert rb.main(["--db", str(db), "brief"]) == 0
    brief = capsys.readouterr().out
    assert "## Decisions" in brief
    assert "## Open loops" in brief
    assert "broke prod" in brief
    assert "Acme" in brief


def test_recall_miss(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "Hello", "world"])
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recall", "xyzzy-no-such"]) == 1
    assert "no matches" in capsys.readouterr().out


def test_empty_recent_and_brief(tmp_path, capsys):
    db = tmp_path / "notes.db"
    assert rb.main(["--db", str(db), "recent"]) == 0
    assert "no notes" in capsys.readouterr().out
    assert rb.main(["--db", str(db), "brief"]) == 0
    assert "No notes" in capsys.readouterr().out


def test_unicode_notes(tmp_path, capsys):
    db = tmp_path / "notes.db"
    assert rb.main(["--db", str(db), "add", "日本語メモ", "絵文字 ✅ を含む。", "--tags", "ja"]) == 0
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recall", "絵文字"]) == 0
    out = capsys.readouterr().out
    assert "日本語メモ" in out
    assert "✅" in out


def test_recall_json(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "Auth timeout", "details here", "--tags", "auth"])
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recall", "timeout", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["title"] == "Auth timeout"
    assert data[0]["tags"] == "auth"


def test_invalid_limit(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "Hello", "world"])
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recent", "--limit", "0"]) == 1
    assert "limit must be positive" in capsys.readouterr().err
    assert rb.main(["--db", str(db), "recent", "--limit", "-3"]) == 1


def test_tags_search(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "One", "body", "--tags", "billing"])
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recall", "billing"]) == 0
    assert "One" in capsys.readouterr().out


def test_special_fts_chars_fall_back(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "Quote note", 'He said "timeout" happened.'])
    capsys.readouterr()
    # A dangling quote would break MATCH; LIKE fallback should still find it or return no crash.
    code = rb.main(["--db", str(db), "recall", '"timeout'])
    assert code in (0, 1)
    captured = capsys.readouterr()
    assert "error:" not in captured.err


def test_custom_kind_in_brief(tmp_path, capsys):
    db = tmp_path / "notes.db"
    # --kind is restricted to note/decision/open; write a custom kind through the API
    conn = rb.open_db(db)
    try:
        rb.add_note(conn, "Spike", "Tried a spike.", "research", "lab")
    finally:
        conn.close()
    assert rb.main(["--db", str(db), "brief"]) == 0
    out = capsys.readouterr().out
    assert "## research" in out
    assert "Spike" in out


def test_recent_order(tmp_path, capsys):
    db = tmp_path / "notes.db"
    rb.main(["--db", str(db), "add", "First", "a"])
    rb.main(["--db", str(db), "add", "Second", "b"])
    capsys.readouterr()
    assert rb.main(["--db", str(db), "recent", "--limit", "10"]) == 0
    out = capsys.readouterr().out
    assert out.index("Second") < out.index("First")


def test_add_without_body(tmp_path, capsys):
    db = tmp_path / "notes.db"
    assert rb.main(["--db", str(db), "add", "Title only"]) == 0
    assert "added #" in capsys.readouterr().out
    assert rb.main(["--db", str(db), "recent"]) == 0
    assert "Title only" in capsys.readouterr().out
