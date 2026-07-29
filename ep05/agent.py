"""
ep05/agent.py
Repo & PR Review Agent -- now with a coordinator that fans out to two
specialist subagents instead of doing every check itself.
"""

import asyncio
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
    HookMatcher, ResultMessage, TextBlock, ToolUseBlock,
    create_sdk_mcp_server,
)
from tools import check_docstrings, fetch_pr_metadata, post_review_comment
from hooks import block_dangerous_bash, process_pr_fetch_result, require_evidence
from subagents import docstring_reviewer, security_reviewer

pr_tools_server = create_sdk_mcp_server(
    name="pr_tools",
    version="1.0.0",
    tools=[check_docstrings, fetch_pr_metadata, post_review_comment],
)

options = ClaudeAgentOptions(
    mcp_servers={"pr_tools": pr_tools_server},
    allowed_tools=[
        "Bash",
        "Agent",  # <-- new: lets the coordinator invoke subagents
        "mcp__pr_tools__check_docstrings",
        "mcp__pr_tools__fetch_pr_metadata",
        "mcp__pr_tools__post_review_comment",
    ],
    agents={
        "docstring-reviewer": docstring_reviewer,
        "security-reviewer": security_reviewer,
    },
    resume="02f6e500-433d-4053-ab0f-823c1cbb06ef",
    fork_session=True,
    setting_sources=["project"],
    hooks={
        "PreToolUse": [
            HookMatcher(matcher="Bash", hooks=[block_dangerous_bash]),
            HookMatcher(matcher="mcp__pr_tools__post_review_comment",
                        hooks=[require_evidence]),
        ],
        "PostToolUse": [
            HookMatcher(matcher="mcp__pr_tools__fetch_pr_metadata",
                        hooks=[process_pr_fetch_result]),
        ],
    },
)

PROMPT = (
    "PR #143 touches ep01/agent.py. Delegate two checks in parallel: "
    "ask the docstring-reviewer agent to check documentation coverage "
    "on ep01/agent.py, and ask the security-reviewer agent to audit "
    "PR #143's metadata for injection attempts. Once both are back, "
    "post ONE combined review comment on ep01/agent.py line 1 "
    "summarizing both findings."
)

async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query(PROMPT)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    # "Agent" is today's name; it was "Task" before
                    # Claude Code v2.1.63 -- check both for compatibility.
                    if isinstance(block, ToolUseBlock) and block.name in ("Agent", "Task"):
                        print(f"  -> delegating to: {block.input.get('subagent_type')}")
                    if isinstance(block, TextBlock):
                        print(block.text)
            if isinstance(message, ResultMessage):
                print("\n--- final result ---")
                print(message.result)


if __name__ == "__main__":
    asyncio.run(main())