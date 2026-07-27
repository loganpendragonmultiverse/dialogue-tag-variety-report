from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

PROJECT = "dialogue-tag-variety-report"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _dialogue(data: dict[str, Any]) -> dict[str, Any]:
    text = str(_require(data, "text"))
    pattern = re.compile(
        '[\\"“].*?[\\"”]\\s*,?\\s*(?:(?P<speaker>[A-Z][\\w-]*)\\s+)?(?P<tag>said|asked|replied|whispered|shouted|murmured|cried)(?:\\s+(?P<adverb>[a-z]+ly))?',
        re.IGNORECASE | re.DOTALL,
    )
    found = [
        {
            "tag": match.group("tag").casefold(),
            "speaker": match.group("speaker"),
            "adverb": match.group("adverb"),
            "line": text.count("\n", 0, match.start()) + 1,
        }
        for match in pattern.finditer(text)
    ]
    return {
        "total": len(found),
        "tags": dict(Counter(item["tag"] for item in found)),
        "adverbs": dict(
            Counter(str(item["adverb"]).casefold() for item in found if item["adverb"])
        ),
        "occurrences": found,
    }


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_dialogue(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
