import json
from pathlib import Path

import pytest

from dialogue_tag_variety_report.cli import main
from dialogue_tag_variety_report.core import PROJECT, analyze, render_json, render_markdown


def test_representative_sample_has_expected_result():
    data = json.loads(
        (Path(__file__).parents[1] / "examples" / "sample.json").read_text(encoding="utf-8")
    )
    report = analyze(data)
    assert report["version"] == 1
    assert report["project"] == PROJECT
    assert report["tags"] == {"said": 2, "asked": 1}
    assert report["speakers"] == {"Mara": {"said": 2}, "Ivo": {"asked": 1}}
    assert report["sections"] == {"Arrival": {"said": 1, "asked": 1}, "Decision": {"said": 1}}
    assert f'"project": "{PROJECT}"' in render_json(report)
    assert PROJECT.replace("-", " ").title() in render_markdown(report)


def test_missing_required_input_is_rejected():
    with pytest.raises(ValueError):
        analyze({})


def test_custom_catalog_and_markdown_sections():
    report = analyze(
        {
            "tags": ["observed", "said"],
            "text": '# Opening\n"Look," Mina observed.\n## Turn\n"Go," said quietly.',
        }
    )
    assert report["catalog"] == ["observed", "said"]
    assert report["sections"] == {"Opening": {"observed": 1}, "Turn": {"said": 1}}
    assert report["speakers"]["(unknown)"] == {"said": 1}
    assert report["occurrences"][1]["section"] == "Turn"
    with pytest.raises(ValueError):
        analyze({"text": '"Hi," Jo said.', "tags": []})


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["project"] == PROJECT
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
