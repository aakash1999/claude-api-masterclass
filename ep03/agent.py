import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)

from tools import review_tools

PROMPT = (
    "Check docstring coverage on ep01/agent.py and ep02/agent.py. "
    "For each file, tell me what's missing and whether it's worth fixing "
    "before merging."
)

options = ClaudeAgentOptions(
    model="claude-sonnet-5",
    mcp_servers={"review-tools": review_tools},
    tools=[],  # no built-ins in Claude's context -- only our custom tool is visible
    allowed_tools=["mcp__review-tools__check_docstring_coverage"],
    system_prompt="You are a senior Python reviewer. Be concise and specific.",
    max_turns=6,
)

async def main():
    async for message in query(prompt=PROMPT, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[tool call] {block.name}({block.input})")
                elif isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            cost = message.total_cost_usd or 0.0
            print(
                f"\n--- {message.num_turns} turn(s) . "
                f"${cost:.4f} . error={message.is_error} ---"
            )


if __name__ == "__main__":
    anyio.run(main)