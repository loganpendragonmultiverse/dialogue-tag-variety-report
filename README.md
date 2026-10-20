# Dialogue Tag Variety Report

[![CI](https://github.com/loganpendragonmultiverse/dialogue-tag-variety-report/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/dialogue-tag-variety-report/actions/workflows/ci.yml)

Count dialogue tags and nearby adverbs so writers can review repetition without prescribing style. The command runs locally, uses explicit UTF-8 JSON input, and produces deterministic JSON or Markdown reports without modifying the supplied source material.

## Three-minute start

```bash
python -m pip install .
dialogue-tags examples/sample.json
dialogue-tags examples/sample.json --format json --output report.json
```

The example documents the complete input shape. Supply an optional `tags` array to replace the seven-tag default catalog. Reports include tag totals, nearby adverbs, per-speaker counts, and counts grouped under Markdown headings. Markdown is intended for immediate review; JSON preserves structured evidence for scripts and later comparison. An existing output file is never overwritten.

## Privacy and platforms

All manuscript text stays local.

Python 3.10 or newer is supported on Windows, macOS, and Linux. The package has no runtime dependencies, telemetry, account, or hosted service.

## Interpretation boundary

The parser recognizes common quoted-dialogue patterns. Counts are descriptive—not style prescriptions—and will miss unconventional punctuation or tags separated from dialogue. Speaker detection is intentionally narrow; unmatched speakers are reported as `(unknown)`.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

Version 1.1 adds editable tag catalogs plus speaker and Markdown-section aggregation. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.2.0: tags before dialogue

Set `include_pre_dialogue` to `true` to recognize forms such as `Mara said, “Hello.”` and `Mara asked: "Why?"`, including multiline quotes and custom multiword tags. In this mode every occurrence includes `position` (`pre` or `post`) and a half-open `tag_span` in the original text, counting Unicode characters. Matches sharing the same tag span count once. Results follow tag position in source order. The default post-quote parser and report fields remain unchanged. Speaker recognition still accepts one word; this is a punctuation heuristic, not character inference.

Try the synthetic example:

```bash
dialogue-tags examples/feature.json --format json
```

## Version 1.2.1 maintenance

Tags and nearby adverbs match whole words; single-word speakers may start with a Unicode letter. Tags follow a complete, consistently paired straight or curly quote. Each quote pair is inspected independently; unrelated earlier quotes and tags in later paragraphs are not joined. Only horizontal spaces may separate a closing quote and its tag. This remains a narrow punctuation heuristic: escaped or nested quotation marks and multiword speaker names are outside its interpretation scope. Occurrence lines and sections use the same Python `splitlines` boundaries, including LF, CRLF, CR and Unicode line separators; tag spans keep original character coordinates.

Input must be a JSON object with a nonempty text string; custom catalog entries must be strings and `include_pre_dialogue` must be a boolean. Malformed inputs produce an error and exit status 2. Markdown evidence uses a fence longer than any backticks in section names.

Output files are created exclusively, rejecting existing files, dangling symbolic links and files created before creation. Inputs are never rewritten. This does not promise an atomic defense against replacement of an output leaf or parent directory by a hostile process.

Custom tag matching retains the original trimmed spelling and Python Unicode case-insensitive regex semantics; catalog labels and reported tag keys remain case-folded. Multi-character case-fold expansions are not inferred as equivalent literal spellings. Duplicate normalized catalog labels retain the first supplied spelling for matching.
