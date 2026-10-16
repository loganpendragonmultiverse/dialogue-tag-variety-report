# Testing

Install development tools with `python -m pip install -e ".[dev]"`.

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Preserve the coverage gate and supported CI matrix.

## Version 1.2.0 acceptance

`tests/test_feature.py` covers the new option, boundary cases, and unchanged default reports using synthetic text only. Run `dialogue-tags examples/feature.json --format json` and the README sample commands against an installed wheel and an extracted source archive. Inspect packaged README, CHANGELOG, DEVELOPMENT and TESTING documents and confirm package version 1.2.0.
