from pathlib import Path
import retainbook.cli as rb


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
