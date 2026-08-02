"""One-off: print the context window breakdown. Not part of the agent."""

import asyncio

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient


async def main():
    options = ClaudeAgentOptions(
        setting_sources=["project"],
        allowed_tools=["Read", "Grep", "Glob"],
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("In one sentence, what does this project do?")
        async for _ in client.receive_response():
            pass

        usage = await client.get_context_usage()
        print(f"{usage['totalTokens']:,} / {usage['maxTokens']:,} tokens "
              f"({usage['percentage']:.1f}%)")
        print(f"raw window: {usage['rawMaxTokens']:,}")
        print(f"autocompact: {usage['isAutoCompactEnabled']}  "
              f"threshold: {usage.get('autoCompactThreshold')}")
        for cat in sorted(usage["categories"], key=lambda c: -c["tokens"]):
            print(f"  {cat['name']:<26}{cat['tokens']:>9,}")


asyncio.run(main())