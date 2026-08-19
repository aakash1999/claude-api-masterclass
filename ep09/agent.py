"""PR & Repo Review Agent — Episode 09: MCP in the real world.

Run this from inside `ep09/`. Same cwd rule as every episode since Ep06:
CLAUDE.md, Skills, and -- new this episode -- .mcp.json are all discovered
starting from the working directory, gated by the same setting_sources=
["project"] switch we flipped on back in Episode 06. We didn't know it
yet at the time, but that one line was already doing double duty.

What changed since Ep08: two new MCP servers exist on disk (see .mcp.json),
but NEITHER is wired into review_pr()'s subagent flow. The mock
fetch_pr_metadata from Ep04 is still exactly what docstring-reviewer and
security-reviewer call for PR #143 -- deterministic, offline, safe to
re-run on camera as many times as a retake needs. The two new servers are
a separate, opt-in capability that only the coordinator gets, and only
when asked for:

  - "github"     -- GitHub's real, official remote MCP server, configured
                    in .mcp.json (type "http"). Lets the coordinator
                    answer questions against REAL GitHub data on request.
  - "repo_facts" -- our own standalone MCP server, also in .mcp.json
                    (type "stdio"), living at ep09/repo_facts_server.py.
                    Counts TODO/FIXME comments. A genuinely separate
                    program -- Claude Code, Claude Desktop, and Cursor
                    could all launch this exact same file too, no Agent
                    SDK involved.

Both live in .mcp.json, not in build_options(). See that file for why:
they're pure config -- a URL, or a command to run -- nothing about them
needs a live Python object the way pr_tools does.
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
    *,
    include_github: bool = False,
) -> ClaudeAgentOptions:
    """Everything Ep01-08 built, plus this episode's two MCP servers.

    include_github defaults to False on purpose. review_pr() below never
    passes True -- a normal PR review has no business depending on
    network access or a GitHub token being present. Only the ad-hoc,
    ask-a-real-question path in main() turns it on.
    """
    allowed_tools = [
        "Agent",
        "Read",
        "Grep",
        "Glob",
        "mcp__pr_tools__check_docstrings",
        "mcp__pr_tools__fetch_pr_metadata",
        "mcp__pr_tools__submit_finding",
        "mcp__pr_tools__publish_review",
        # Ep09 -- our own standalone server, one tool. Naming it
        # explicitly (instead of "mcp__repo_facts__*") costs nothing here
        # and says exactly what's allowed at a glance.
        "mcp__repo_facts__count_todos",
    ]
    if include_github:
        # Ep09 -- scoped to exactly one read-only tool. GitHub's server
        # exposes dozens of tools across toolsets; Ep06 already taught us
        # why we don't hand the model all of them just because they exist.
        allowed_tools.append("mcp__github__pull_request_read")

    return ClaudeAgentOptions(
        # pr_tools carries a live Python object (McpSdkServerConfig's
        # `instance` field) -- that can ONLY be passed here, in code.
        # "github" and "repo_facts" are pure config -- a URL, or a command
        # to run -- so they live in .mcp.json instead, picked up
        # automatically because setting_sources includes "project".
        mcp_servers={"pr_tools": pr_tools},
        agents=REVIEW_AGENTS,
        allowed_tools=allowed_tools,
        skills=["pr-digest", "changelog-entry"],
        setting_sources=["project"],
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

    Unchanged since Ep08 -- this is still the mock fetch_pr_metadata path,
    and include_github is never passed here. A PR review's reliability
    shouldn't depend on GitHub's servers being reachable.
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


async def ask_about_live_repo(question: str) -> None:
    """Ep09 -- a separate, one-off entry point that turns GitHub ON.

    No PR number, no resume, no findings -- this deliberately never
    touches review_pr()'s session index. It's a different job: one live
    question against real GitHub data, using the same coordinator setup
    with a single flag flipped.
    """
    options = build_options(include_github=True)
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


async def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        question = " ".join(sys.argv[2:]) or (
            "What are the 3 most recently updated open pull requests on "
            "anthropics/claude-agent-sdk-python?"
        )
        await ask_about_live_repo(question)
        return

    pr_number = int(sys.argv[1]) if len(sys.argv) > 1 else 143
    prompt = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"Review PR #{pr_number}. Fan out to both reviewers, then post one comment."
    )
    await review_pr(pr_number, prompt)


if __name__ == "__main__":
    asyncio.run(main())
