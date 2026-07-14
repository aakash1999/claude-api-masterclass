import anyio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

PROMPT = (
    "Read ep01/agent.py and give me a 3-bullet "
    "plain-English summary of what it does."
)

options = ClaudeAgentOptions(
    model="claude-sonnet-5",
    allowed_tools=["Read"],
    cwd="../",  # repo root -- lets Claude reach ep01/agent.py
    system_prompt="You are a senior Python reviewer. Be concise.",
    max_turns=5,
)

async def main():
    async for message in query(prompt=PROMPT, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            cost = message.total_cost_usd or 0.0
            print(
                f"\n--- {message.num_turns} turn(s) . "
                f"${cost:.4f} . error={message.is_error} ---"
            )


if __name__ == "__main__":
    anyio.run(main)