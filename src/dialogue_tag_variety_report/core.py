from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

PROJECT = "dialogue-tag-variety-report"
DEFAULT_TAGS = ("said", "asked", "replied", "whispered", "shouted", "murmured", "cried")


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _catalog(data: dict[str, Any]) -> list[str]:
    raw_tags = data.get("tags", list(DEFAULT_TAGS))
    if not isinstance(raw_tags, list) or not raw_tags:
        raise ValueError("tags must be a non-empty list")
    tags: list[str] = []
    for raw_tag in raw_tags:
        tag = str(raw_tag).strip().casefold()
        if not tag or len(tag) > 80 or not re.fullmatch(r"[\w -]+", tag):
            raise ValueError("tags must contain words, spaces, or hyphens")
        if tag not in tags:
            tags.append(tag)
    return tags


def _dialogue(data: dict[str, Any]) -> dict[str, Any]:
    text = str(_require(data, "text"))
    include_pre = data.get("include_pre_dialogue", False)
    if not isinstance(include_pre, bool):
        raise TypeError("include_pre_dialogue must be a boolean")
    tags = _catalog(data)
    tag_pattern = "|".join(re.escape(tag) for tag in sorted(tags, key=len, reverse=True))
    pattern = re.compile(
        rf'["\u201c].*?["\u201d]\s*,?\s*'
        rf"(?:(?P<speaker>[A-Z][\w-]*)\s+)?(?P<tag>{tag_pattern})"
        r"(?:\s+(?P<adverb>[a-z]+ly))?",
        re.IGNORECASE | re.DOTALL,
    )
    headings: list[tuple[int, str]] = [(1, "(document)")]
    for line_number, line_text in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line_text)
        if heading:
            headings.append((line_number, heading.group(1)))

    def section_at(line: int) -> str:
        return next(name for start, name in reversed(headings) if start <= line)

    found: list[dict[str, Any]] = []
    matches = [(match, "post") for match in pattern.finditer(text)]
    if include_pre:
        pre_pattern = re.compile(
            rf"(?<!\w)(?P<speaker>[A-Z][\w-]*)\s+(?P<tag>{tag_pattern})(?!\w)"
            r"(?:\s+(?P<adverb>[a-z]+ly))?\s*[,:]\s*"
            r'(?P<dialogue>"[^"]*"|“[^”]*”)',
            re.IGNORECASE | re.DOTALL,
        )
        matches.extend((match, "pre") for match in pre_pattern.finditer(text))
        matches.sort(key=lambda item: item[0].start("tag"))
    seen: set[tuple[int, int]] = set()
    for match, position in matches:
        tag_span = match.span("tag")
        if tag_span in seen:
            continue
        seen.add(tag_span)
        line = text.count("\n", 0, match.start()) + 1
        found.append(
            {
                "tag": match.group("tag").casefold(),
                "speaker": match.group("speaker"),
                "adverb": match.group("adverb"),
                "line": line,
                "section": section_at(line),
            }
        )

        if include_pre:
            found[-1]["position"] = position
            found[-1]["tag_span"] = {"start": tag_span[0], "end": tag_span[1]}
    speaker_counts: dict[str, Counter[str]] = {}
    section_counts: dict[str, Counter[str]] = {}
    for item in found:
        speaker = str(item["speaker"] or "(unknown)")
        speaker_counts.setdefault(speaker, Counter())[str(item["tag"])] += 1
        section_counts.setdefault(str(item["section"]), Counter())[str(item["tag"])] += 1
    return {
        "total": len(found),
        "catalog": tags,
        "tags": dict(Counter(str(item["tag"]) for item in found)),
        "speakers": {speaker: dict(counts) for speaker, counts in speaker_counts.items()},
        "sections": {section: dict(counts) for section, counts in section_counts.items()},
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
