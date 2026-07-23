import asyncio
from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ClaudeSDKClient,
    HookMatcher, ResultMessage, TextBlock, create_sdk_mcp_server,
)
from tools import check_docstrings, fetch_pr_metadata, post_review_comment
from hooks import block_dangerous_bash, process_pr_fetch_result, require_evidence

pr_tools_server = create_sdk_mcp_server(
    name="pr_tools",
    version="1.0.0",
    tools=[check_docstrings, fetch_pr_metadata, post_review_comment],
)

options = ClaudeAgentOptions(
    mcp_servers={"pr_tools": pr_tools_server},
    allowed_tools=[
        "Bash",
        "mcp__pr_tools__check_docstrings",
        "mcp__pr_tools__fetch_pr_metadata",
        "mcp__pr_tools__post_review_comment",
    ],
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


async def main():
    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            "Review PR #143. Fetch its metadata first, then post one "
            "review comment citing a specific file and line."
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                print(f"\n[done] turns={message.num_turns} "
                      f"permission_denials={message.permission_denials}")


if __name__ == "__main__":
    asyncio.run(main())