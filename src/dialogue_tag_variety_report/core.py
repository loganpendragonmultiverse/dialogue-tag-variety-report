from __future__ import annotations

import json
import re
from bisect import bisect_right
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
        if not isinstance(raw_tag, str):
            raise TypeError("tags must contain strings")
        tag = raw_tag.strip().casefold()
        if not tag or len(tag) > 80 or not re.fullmatch(r"[\w -]+", tag):
            raise ValueError("tags must contain words, spaces, or hyphens")
        if tag not in tags:
            tags.append(tag)
    return tags


def _dialogue(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TypeError("input must be an object with a text string")
    text = _require(data, "text")
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    include_pre = data.get("include_pre_dialogue", False)
    if not isinstance(include_pre, bool):
        raise TypeError("include_pre_dialogue must be a boolean")
    tags = _catalog(data)
    tag_pattern = "|".join(re.escape(tag) for tag in sorted(tags, key=len, reverse=True))
    quotes = list(re.finditer(r'"[^"]*"|“[^”]*”', text))
    post_pattern = re.compile(
        rf"[ \t]*,?[ \t]*(?:(?P<speaker>[^\W\d_][\w-]*)[ \t]+)?"
        rf"(?P<tag>{tag_pattern})(?!\w)(?:[ \t]+(?P<adverb>[a-z]+ly)(?!\w))?",
        re.IGNORECASE,
    )
    line_starts = [0]
    for source_line in text.splitlines(keepends=True):
        line_starts.append(line_starts[-1] + len(source_line))
    headings: list[tuple[int, str]] = [(1, "(document)")]
    for line_number, line_text in enumerate(text.splitlines(), start=1):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line_text)
        if heading:
            headings.append((line_number, heading.group(1)))

    def section_at(line: int) -> str:
        return next(name for start, name in reversed(headings) if start <= line)

    found: list[dict[str, Any]] = []
    matches = []
    for quote in quotes:
        post = post_pattern.match(text, quote.end())
        if post is not None:
            matches.append((post, "post", quote.start()))
    if include_pre:
        pre_pattern = re.compile(
            rf"(?<!\w)(?P<speaker>[^\W\d_][\w-]*)[ \t]+(?P<tag>{tag_pattern})(?!\w)"
            r"(?:[ \t]+(?P<adverb>[a-z]+ly)(?!\w))?[ \t]*[,:][ \t]*$",
            re.IGNORECASE,
        )
        previous_end = 0
        for quote in quotes:
            pre = pre_pattern.search(text, previous_end, quote.start())
            if pre is not None:
                matches.append((pre, "pre", pre.start()))
            previous_end = quote.end()
        matches.sort(key=lambda item: item[0].start("tag"))
    seen: set[tuple[int, int]] = set()
    for match, position, occurrence_start in matches:
        tag_span = match.span("tag")
        if tag_span in seen:
            continue
        seen.add(tag_span)
        line = bisect_right(line_starts, occurrence_start)
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
            payload = json.dumps(value, indent=2, ensure_ascii=False)
            fence = "`" * max(
                3, max((len(run) for run in re.findall(r"`+", payload)), default=0) + 1
            )
            lines.append(f"{fence}json\n{payload}\n{fence}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
