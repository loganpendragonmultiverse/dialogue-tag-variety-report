from copy import deepcopy

import pytest

from dialogue_tag_variety_report.core import analyze


@pytest.mark.parametrize("quote", [('"', '"'), ("“", "”")])
@pytest.mark.parametrize("punctuation", [",", ":"])
def test_pre_post_multiline_and_spans(quote, punctuation):
    left, right = quote
    text = (
        f"# Scene\nMara said{punctuation} {left}Hello,\nworld!{right}\n{left}Why?{right} Ivo asked."
    )
    data = {"text": text}
    original = deepcopy(data)
    baseline = analyze(data)
    result = analyze({**data, "include_pre_dialogue": True})
    assert data == original
    assert baseline["tags"] == {"asked": 1}
    assert result["tags"] == {"said": 1, "asked": 1}
    assert [item["position"] for item in result["occurrences"]] == ["pre", "post"]
    for item in result["occurrences"]:
        span = item["tag_span"]
        assert text[span["start"] : span["end"]].casefold() == item["tag"]
    assert result["sections"] == {"Scene": {"said": 1, "asked": 1}}


def test_multiword_tags_adverbs_and_deduplication():
    text = "Mara said softly, “One.” Mara went on: “Two.”\n“Three,” Mara said, “Four.”"
    data = {"text": text, "tags": ["said", "went on"], "include_pre_dialogue": True}
    result = analyze(data)
    assert result["tags"] == {"said": 2, "went on": 1}
    assert result["adverbs"] == {"softly": 1}
    spans = [tuple(item["tag_span"].values()) for item in result["occurrences"]]
    assert len(spans) == len(set(spans)) == 3
    assert analyze({"text": text}) == analyze({"text": text, "include_pre_dialogue": False})
    assert analyze({"text": "Mara saidness, “Hello.”", "include_pre_dialogue": True})["total"] == 0
    with pytest.raises(TypeError, match="boolean"):
        analyze({"text": text, "include_pre_dialogue": "yes"})
