"""Sample module used as a target for the PR & Repo Review Agent.

Two trivial utilities -- one with a complete docstring, one without --
so the docstring-reviewer subagent has at least one real finding to
flag during a smoke test of the Ep09 review flow.

Nothing here is security-sensitive. No I/O, no shell calls, no parsing
of untrusted input. Just plain math.
"""

from __future__ import annotations


def average(values: list[float]) -> float:
    """Return the arithmetic mean of ``values``.

    Args:
        values: Non-empty list of numbers to average. An empty list is
            treated as zero so callers don't have to special-case it --
            matches the behavior of the legacy ``stats.mean`` shim this
            function replaced.

    Returns:
        The arithmetic mean. ``0.0`` for an empty input.
    """
    if not values:
        return 0.0
    return sum(values) / len(values)


def find_extreme(values):
    if not values:
        return None
    return min(values), max(values)
