import json

import pytest

from dialogue_tag_variety_report.cli import main
from dialogue_tag_variety_report.core import analyze, render_markdown


def test_complete_tag_words_and_independent_quote_pairs():
    text = '"First." She left.\n"Second." Mara saidness.\n"Third." Ivo said.'
    report = analyze({"text": text})
    assert report["tags"] == {"said": 1}
    assert report["occurrences"][0]["speaker"] == "Ivo"
    assert report["occurrences"][0]["line"] == 3


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r"])
def test_line_endings_and_no_distant_post_quote_tags(ending):
    text = '# Start\n"No tag."\n\nMara said.\n# Next\n"Here." Ivo asked.'.replace("\n", ending)
    report = analyze({"text": text})
    assert report["tags"] == {"asked": 1}
    assert report["occurrences"][0]["line"] == 6
    assert report["sections"] == {"Next": {"asked": 1}}


@pytest.mark.parametrize(
    "bad",
    [
        None,
        [],
        7,
        {"text": 7},
        {"text": False},
        {"text": {}},
        {"text": "x", "tags": [7]},
        {"text": "x", "include_pre_dialogue": "true"},
    ],
)
def test_bad_typed_input_is_cli_error_without_output(tmp_path, capsys, bad):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(bad), encoding="utf-8")
    output = tmp_path / "report.json"
    assert main([str(source), "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert captured.out == "" and "error:" in captured.err
    assert not output.exists()


def test_markdown_fences_untrusted_section_names():
    report = analyze({"text": '# Scene```\n"Hello." Mara said.'})
    assert "````json" in render_markdown(report)
