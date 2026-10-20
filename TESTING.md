# Testing

Install development tools with `python -m pip install -e ".[dev]"`.

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Preserve the coverage gate and supported CI matrix.

## Version 1.2.0 acceptance

`tests/test_feature.py` covers the new option, boundary cases, and unchanged default reports using synthetic text only. Run `dialogue-tags examples/feature.json --format json` and the README sample commands against an installed wheel and an extracted source archive. Inspect packaged README, CHANGELOG, DEVELOPMENT and TESTING documents and confirm package version 1.2.0.

## 1.2.1 acceptance

Run the full suite with the unchanged 90% combined statement/branch coverage gate. New regressions exercise exclusive report creation, dangling links, invalid UTF-8 and source preservation. Install both built distributions into isolated targets, verify module origins outside the checkout, run the full suite and documented CLI examples, and inspect all four packaged handoff documents.
