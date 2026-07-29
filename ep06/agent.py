"""PR & Repo Review Agent — Episode 06: memory, sessions, and context that survives.

Run this from inside `ep06/`. Two reasons, both load-bearing:
  1. CLAUDE.md is discovered from the working directory upward.
  2. Session transcripts are keyed by working directory, so `resume` from a
     different cwd silently starts a brand new conversation.
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
from tools import check_docstrings, fetch_pr_metadata, post_review_comment

pr_tools = create_sdk_mcp_server(
    name="pr_tools",
    version="1.0.0",
    tools=[check_docstrings, fetch_pr_metadata, post_review_comment],
)


def build_options(
    resume_id: str | None = None,
    fork: bool = False,
) -> ClaudeAgentOptions:
    """Everything Ep01-05 built, plus this episode's three memory settings."""
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
            "mcp__pr_tools__post_review_comment",
        ],
        # NEW — without "project" in this list, CLAUDE.md is never loaded.
        setting_sources=["project"],
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
            # NEW — fires when the SDK is about to summarize the conversation.
            "PreCompact": [HookMatcher(hooks=[log_precompact])],
        },
        # NEW — resume is None on a first run, which the SDK reads as "fresh".
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
    """Review a PR, resuming the previous session for that PR when we have one."""
    prior = None if fresh else get_session_id(pr_number)
    if prior:
        print(f"-> resuming session {prior[:8]} for PR #{pr_number}")
    else:
        print(f"-> new session for PR #{pr_number}")

    session_id = None
    try:
        async for message in query(prompt=prompt, options=build_options(prior, fork)):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                # Present on EVERY result, success or error. This is the one
                # field you must not lose.
                session_id = message.session_id
    except Exception as error:
        # A single-shot query() raises after yielding an error result, so the
        # id above was already captured if a result came back at all.
        print(f"[error] {error}")

    if session_id is None:
        return None

    if fork:
        # The fork gets its own id; the original history is untouched. We keep
        # pointing at the original so the main thread stays the main thread.
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