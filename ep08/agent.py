"""PR & Repo Review Agent — Episode 08: reusable Skills, chained.

Run this from inside `ep08/`. Two reasons, both load-bearing:
  1. CLAUDE.md is discovered from the working directory upward.
  2. Skills are discovered the same way — from `.claude/skills/` in the
     working directory and every parent up to the repository root.
Session transcripts are also keyed by working directory, so `resume` from a
different cwd silently starts a brand new conversation.

What changed since Ep07: two Skills now live on disk — `pr-digest` and
`changelog-entry` (see `.claude/skills/`). Neither is wired into the review
flow itself; they're on-demand, chained on top of a review that's already
been published. This file's only change is `build_options()` turning them on.
"""

import asyncio
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
)

from hooks import (
    block_dangerous_bash,
    log_precompact,
    process_pr_fetch_result,
    require_evidence,
)
from session_index import get_session_id, remember_session
from subagents import REVIEW_AGENTS
from tools import (
    check_docstrings,
    fetch_pr_metadata,
    publish_review,
    reset_findings,
    submit_finding,
)

pr_tools = create_sdk_mcp_server(
    name="pr_tools",
    version="1.0.0",
    tools=[check_docstrings, fetch_pr_metadata, submit_finding, publish_review],
)


def build_options(
    resume_id: str | None = None,
    fork: bool = False,
) -> ClaudeAgentOptions:
    """Everything Ep01-07 built, plus this episode's two Skills."""
    return ClaudeAgentOptions(
        mcp_servers={"pr_tools": pr_tools},
        agents=REVIEW_AGENTS,
        allowed_tools=[
            "Agent",
            "Read",
            "Grep",
            "Glob",
            "mcp__pr_tools__check_docstrings",
            "mcp__pr_tools__fetch_pr_metadata",
            "mcp__pr_tools__submit_finding",
            "mcp__pr_tools__publish_review",
        ],
        # Ep08 -- the single place to turn Skills on. Checked directly
        # against installed claude-agent-sdk 0.2.128 source (types.py,
        # subprocess_cli.py): setting this ALSO grants the tool access each
        # Skill needs -- it appends Skill(pr-digest) and Skill(changelog-entry)
        # to the *effective* allowed_tools sent to the CLI, on top of the
        # list above. Do NOT also add "Skill" to allowed_tools yourself --
        # the SDK source marks passing "Skill" there directly as deprecated
        # now that this option exists to do it for you.
        skills=["pr-digest", "changelog-entry"],
        # Ep06 — without "project" in this list, CLAUDE.md is never loaded.
        # Also required for Skill discovery. Confirmed in source: the SDK
        # only *defaults* setting_sources to ["user", "project"] when it's
        # unset -- since we set it ourselves, our explicit list is left alone.
        setting_sources=["project"],
        # Ep08 -- this review runs headless; nobody's at a terminal to click
        # "approve." "dontAsk" denies anything outside allowed_tools instead
        # of prompting for it (and prompting for it here would just hang).
        permission_mode="dontAsk",
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[block_dangerous_bash]),
            ],
            "PostToolUse": [
                HookMatcher(
                    matcher="mcp__pr_tools__fetch_pr_metadata",
                    hooks=[process_pr_fetch_result],
                ),
            ],
            "Stop": [HookMatcher(hooks=[require_evidence])],
            "PreCompact": [HookMatcher(hooks=[log_precompact])],
        },
        # Ep06 — resume is None on a first run, which the SDK reads as "fresh".
        resume=resume_id,
        fork_session=fork,
    )


async def review_pr(
    pr_number: int,
    prompt: str,
    *,
    fresh: bool = False,
    fork: bool = False,
) -> str | None:
    """Review a PR, resuming the previous session for that PR when we have one.

    Also how this episode's two Skills get exercised -- a `prompt` that just
    asks for a digest and a changelog entry, resumed against a PR session
    that already has a published review sitting in its transcript, needs no
    change here at all. `reset_findings()` clears the module-level
    `_FINDINGS` list either way -- that list is a call-scoped cache purely
    for `publish_review` to build a comment from *this run's* findings; it
    is not where the digest Skill reads from. The digest reads the actual
    resumed conversation transcript, which the SDK reloads independently of
    anything in our own Python process.
    """
    prior = None if fresh else get_session_id(pr_number)
    if prior:
        print(f"-> resuming session {prior[:8]} for PR #{pr_number}")
    else:
        print(f"-> new session for PR #{pr_number}")

    reset_findings()

    session_id = None
    try:
        async for message in query(prompt=prompt, options=build_options(prior, fork)):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                session_id = message.session_id
    except Exception as error:
        print(f"[error] {error}")

    if session_id is None:
        return None

    if fork:
        print(f"-> forked into {session_id[:8]} (original left intact)")
    else:
        remember_session(pr_number, session_id)
        print(f"-> remembered session {session_id[:8]} for PR #{pr_number}")

    return session_id


async def main() -> None:
    pr_number = int(sys.argv[1]) if len(sys.argv) > 1 else 143
    prompt = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"Review PR #{pr_number}. Fan out to both reviewers, then post one comment."
    )
    await review_pr(pr_number, prompt)


if __name__ == "__main__":
    asyncio.run(main())