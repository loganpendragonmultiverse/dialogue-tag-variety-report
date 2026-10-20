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


@pytest.mark.parametrize("ending", ["\n", "\r\n", "\r", "\u2028", "\u0085", "\v"])
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


def test_adverbs_match_complete_words_only():
    result = analyze({"text": '"Hello." Mara said softlyness. "Again." Mara asked rapidly.'})
    assert result["tags"] == {"said": 1, "asked": 1}
    assert result["adverbs"] == {"rapidly": 1}


def test_unicode_letter_initial_speakers_keep_original_spans():
    text = "Éva said, “Hello.”\n“Bye.” Éva asked."
    report = analyze({"text": text, "include_pre_dialogue": True})
    assert report["speakers"] == {"Éva": {"said": 1, "asked": 1}}
    assert [item["line"] for item in report["occurrences"]] == [1, 2]
    for item in report["occurrences"]:
        span = item["tag_span"]
        assert text[span["start"] : span["end"]] == item["tag"]


@pytest.mark.parametrize("tag", ["äußerte", "İ"])
def test_unicode_custom_catalog_matches_original_literal_spelling(tag):
    text = f"Éva {tag}, “Hello.”\n“Bye.” Éva {tag}."
    report = analyze({"text": text, "tags": [tag], "include_pre_dialogue": True})
    assert report["catalog"] == [tag.casefold()]
    assert report["tags"] == {tag.casefold(): 2}
    assert report["speakers"] == {"Éva": {tag.casefold(): 2}}
    assert [item["position"] for item in report["occurrences"]] == ["pre", "post"]
    for item in report["occurrences"]:
        span = item["tag_span"]
        assert text[span["start"] : span["end"]] == tag
