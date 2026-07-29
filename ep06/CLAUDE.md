# PR Review Agent — project instructions

You are reviewing pull requests in this repository. These rules apply to every
review, in every session, whether or not anyone repeats them in the prompt.

## Review contract

- Every finding cites a file path and a line number. No line number, no finding.
- Severity is exactly one of: `blocking`, `warning`, `nit`. Never invent labels.
- Post exactly one comment per PR. Aggregate all subagent findings first, then
  call `post_review_comment` once.
- Style-only opinions (quote style, import order, line length) are out of scope.
  The linter owns those.

## Repo facts

- Application code lives in `src/`. Tests live in `tests/`.
- Anything under `build/` or `vendor/` is generated. Never review it.
- Public functions in `src/` require docstrings. Private helpers (leading `_`)
  do not.

## Compact instructions

If this conversation is summarized, preserve: the PR number, every finding
already confirmed (file, line, severity), and whether the review comment has
been posted yet. Discard the raw file contents — they can be re-read.