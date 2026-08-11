# Ep09 — MCP In The Real World — Snippets Companion

---

## Standalone setup (do this before recording, not on camera)

### 0a — 🧪 terminal, not saved
→ HTML slide 11, "Never Hardcode A Token"

```bash
export GITHUB_PAT="github_pat_xxxxxxxxxxxxxxxxxxxx"
# fine-grained, read-only, scoped to Pull requests, on ONE repo
```

### 0b — ⚠ before you record slide 12/18 — test the headers-expansion gotcha
Not a code block to paste on camera — a check to run privately first. Connect
the `github` server (however your setup normally connects — Claude Code,
or the SDK) with `GITHUB_PAT` set, then confirm the real token is actually
reaching GitHub (a successful `pull_request_read` call, not a 401). If it
silently fails, see slide 12 — this is a real, open bug on some setups, not
a typo on your end. Decide before recording whether you're demonstrating the
working path or narrating the known bug from the docs/issue tracker alone.

---

## Main sequential build

### 1 — 📄 .mcp.json — the GitHub entry
→ HTML slide 10, "Writing .mcp.json — The GitHub Entry"

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Toolsets": "pull_requests"
      }
    }
  }
}
```

### 2 — 📄 agent.py — new allowed_tools entry
→ HTML slide 14, "Scoping Down"

Inside `build_options()`, inside the `if include_github:` block:

```python
if include_github:
    # Ep09 -- scoped to exactly one read-only tool. GitHub's server
    # exposes dozens of tools across toolsets; Ep06 already taught us
    # why we don't hand the model all of them just because they exist.
    allowed_tools.append("mcp__github__pull_request_read")
```

### 3 — 📄 agent.py — build_options() signature
→ HTML slide 17, "Wiring GitHub Into agent.py"

```python
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
```

### 4 — 📄 agent.py — new entry point
→ HTML slide 18, "Demo"

```python
async def ask_about_live_repo(question: str) -> None:
    """Ep09 -- a separate, one-off entry point that turns GitHub ON."""
    options = build_options(include_github=True)
    async for message in query(prompt=question, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
```

### 5 — 🧪 terminal, not saved — the live demo
→ HTML slide 18, "Demo"

⚠ Pre-capture this, per the producer note on slide 18. Real network call,
real token, real repo.

```bash
python agent.py --live "What are the 3 most recently updated open pull \
requests on anthropics/claude-agent-sdk-python?"
```

### 6 — 📄 repo_facts_server.py — the whole file (small enough for one step)
→ HTML slide 21, "Writing repo_facts_server.py With FastMCP"

```python
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_facts")


@mcp.tool()
def count_todos(directory: str = ".") -> str:
    """Count TODO and FIXME comments across every .py file under
    `directory`. Returns a plain-text report: how many were found, and
    each one's file, line number, and the line itself.
    """
    hits = []
    for path in sorted(Path(directory).rglob("*.py")):
        for lineno, line in enumerate(
            path.read_text(errors="ignore").splitlines(), start=1
        ):
            if re.search(r"#\s*(TODO|FIXME)\b", line):
                hits.append(f"{path}:{lineno}  {line.strip()}")
    if not hits:
        return "No TODO or FIXME comments found."
    return f"{len(hits)} found:\n" + "\n".join(hits)


if __name__ == "__main__":
    mcp.run()  # stdio by default -- matches "type": "stdio" in .mcp.json
```

### 7 — 🧪 sanity check, not saved — proving it's really just JSON
→ HTML slide 22, "Proving It's Really Just JSON"

This is a genuine, real terminal session — not illustrative. Save the three
lines below as `mcp_test_input.jsonl` in the same folder as
`repo_facts_server.py`, then pipe it in:

```bash
python repo_facts_server.py < mcp_test_input.jsonl
```

Contents of `mcp_test_input.jsonl` (one JSON object per line):

```json
{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "smoke-test", "version": "0.0.1"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
```

Expected real output (this is what actually came back when this episode
was fact-checked — your `serverInfo.version` may differ slightly depending
on your installed `mcp` package version):

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"repo_facts","version":"1.29.0"}}}
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"count_todos","description":"Count TODO and FIXME comments across every .py file under `directory`. Returns a plain-text report: how many were found, and each one's file, line number, and the line itself.","inputSchema":{"properties":{"directory":{"default":".","title":"Directory","type":"string"}},"title":"count_todosArguments","type":"object"},"outputSchema":{"properties":{"result":{"title":"Result","type":"string"}},"required":["result"],"title":"count_todosOutput","type":"object"}}]}}
```

### 8 — 📄 .mcp.json — both servers together
→ HTML slide 23, "Finishing .mcp.json"

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Toolsets": "pull_requests"
      }
    },
    "repo_facts": {
      "type": "stdio",
      "command": "python",
      "args": ["repo_facts_server.py"]
    }
  }
}
```

---

## Non-runnable illustration blocks (skipped)

⏭ skip — illustrative only, see HTML slide 5 ("Three Ways We've Given
Claude Capabilities"). The recap table of built-in tools vs. in-process
custom tools is a summary of prior episodes' code, not new code to paste —
nothing here belongs in `ep09/`.

⏭ skip — reference only, see HTML slide 8 ("The Four Shapes"). The
`McpStdioServerConfig` / `McpSSEServerConfig` / `McpHttpServerConfig` /
`McpSdkServerConfig` shapes quoted there are read directly from the
installed `claude-agent-sdk` source to prove the mental model on camera —
they're SDK internals, not this project's code, nothing to paste.

⏭ skip — reference only, see HTML slide 12 ("Gotcha: The Headers
Expansion Bug"). The docs-vs-issue-tracker split-screen is a B-ROLL cue,
not code.

---

## Final Files (complete, paste-ready — the source of truth)

### 9 — 📄 .mcp.json — FINAL
→ HTML slide 26, "Final File — .mcp.json"

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}",
        "X-MCP-Toolsets": "pull_requests"
      }
    },
    "repo_facts": {
      "type": "stdio",
      "command": "python",
      "args": ["repo_facts_server.py"]
    }
  }
}
```

### 10 — 📄 agent.py — FINAL
→ HTML slide 27, "Final File — agent.py"

```python
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
```

### 11 — 📄 repo_facts_server.py — FINAL
→ HTML slide 28, "Final File — repo_facts_server.py"

```python
"""Standalone MCP server for the Repo & PR Review Agent project.

This is NOT built with claude_agent_sdk's @tool decorator -- that's the
in-process pattern from Ep03/04 (see tools.py). This is a real, separate
program that speaks MCP over stdio using the actual `mcp` Python SDK
(FastMCP). It has no idea claude-agent-sdk exists. Any MCP client can
talk to it -- Claude Code, Claude Desktop, Cursor, or this Agent SDK
app -- all the same way, all through .mcp.json.

Run standalone (for testing outside any agent):
    python repo_facts_server.py
It'll sit there speaking MCP over stdio -- that's expected, it's waiting
for a client. Ctrl+C to stop. It's meant to be launched BY a client (see
.mcp.json), not run interactively.
"""

import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("repo_facts")


@mcp.tool()
def count_todos(directory: str = ".") -> str:
    """Count TODO and FIXME comments across every .py file under
    `directory`.

    Returns a plain-text report: how many were found, and each one's
    file, line number, and the line itself, so the caller doesn't have
    to go grepping for them by hand.
    """
    hits = []
    for path in sorted(Path(directory).rglob("*.py")):
        for lineno, line in enumerate(
            path.read_text(errors="ignore").splitlines(), start=1
        ):
            if re.search(r"#\s*(TODO|FIXME)\b", line):
                hits.append(f"{path}:{lineno}  {line.strip()}")
    if not hits:
        return "No TODO or FIXME comments found."
    return f"{len(hits)} found:\n" + "\n".join(hits)


if __name__ == "__main__":
    mcp.run()  # stdio by default -- matches "type": "stdio" in .mcp.json
```

---

*Snippets companion — Ep09, Claude Certified Developer, The Build-Along Course.*
