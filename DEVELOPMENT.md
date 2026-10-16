# Development contract

Count dialogue tags and nearby adverbs so writers can review repetition without prescribing style.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, `CHANGELOG.md`, README claims and limitations, repository metadata, release assets, and the Forge catalog together.

## Version 1.2.0

Set `include_pre_dialogue` to `true` to recognize forms such as `Mara said, “Hello.”` and `Mara asked: "Why?"`, including multiline quotes and custom multiword tags. In this mode every occurrence includes `position` (`pre` or `post`) and a half-open `tag_span` in the original text, counting Unicode characters. Matches sharing the same tag span count once. Results follow tag position in source order. The default post-quote parser and report fields remain unchanged. Speaker recognition still accepts one word; this is a punctuation heuristic, not character inference.
