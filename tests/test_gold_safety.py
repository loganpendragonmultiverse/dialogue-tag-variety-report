import json
from pathlib import Path

import pytest

from dialogue_tag_variety_report.cli import main


def test_output_creation_race_preserves_existing_bytes(tmp_path, monkeypatch, capsys):
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"text": '"Hello," Mara said.'}), encoding="utf-8")
    output = tmp_path / "report.json"
    output.write_bytes(b"original")
    original_exists = Path.exists
    monkeypatch.setattr(
        Path, "exists", lambda self: False if self == output else original_exists(self)
    )
    assert main([str(source), "--output", str(output)]) == 2
    assert output.read_bytes() == b"original"
    assert capsys.readouterr().out == ""


def test_dangling_output_link_does_not_create_target(tmp_path, capsys):
    source = tmp_path / "source.json"
    source.write_text(json.dumps({"text": '"Hello," Mara said.'}), encoding="utf-8")
    output = tmp_path / "report.json"
    target = tmp_path / "untouched.json"
    try:
        output.symlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable on this platform: {exc}")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink() and not target.exists()
    assert capsys.readouterr().out == ""


def test_invalid_utf8_is_clean_cli_error(tmp_path, capsys):
    source = tmp_path / "source.json"
    source.write_bytes(b"\xff")
    assert main([str(source)]) == 2
    assert "error:" in capsys.readouterr().err
