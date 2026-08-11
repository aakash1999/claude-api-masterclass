"""Remembers which Agent SDK session reviewed which PR.

This is OUR bookkeeping, not the SDK's `SessionStore` protocol. The SDK already
writes the full transcript to disk at
`~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`. The only thing it cannot
know is which of those sessions belongs to PR #42. That mapping is ours to keep.
"""

import json
from pathlib import Path

INDEX_PATH = Path(__file__).parent / ".pr_sessions.json"


def _load() -> dict[str, str]:
    if not INDEX_PATH.exists():
        return {}
    return json.loads(INDEX_PATH.read_text())


def get_session_id(pr_number: int) -> str | None:
    """Return the session id that last reviewed this PR, or None."""
    return _load().get(str(pr_number))


def remember_session(pr_number: int, session_id: str) -> None:
    """Record the session id so the next review of this PR can resume it."""
    index = _load()
    index[str(pr_number)] = session_id
    INDEX_PATH.write_text(json.dumps(index, indent=2))


def forget_session(pr_number: int) -> None:
    """Drop the mapping so the next review starts from a clean context."""
    index = _load()
    index.pop(str(pr_number), None)
    INDEX_PATH.write_text(json.dumps(index, indent=2))