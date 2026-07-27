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
