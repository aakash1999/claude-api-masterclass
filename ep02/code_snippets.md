
## Standalone / Setup (run before the build section — not part of the sequential session below)

### Step 1 — Install the SDK
🧪 terminal, not saved
→ HTML slide 5

```bash
pip install claude-agent-sdk
```

### Step 2 — Sanity check: your first query() call
🧪 sanity check, not saved
→ HTML slide 8

```python
import anyio
from claude_agent_sdk import query

async def main():
    async for message in query(prompt="What is 2 + 2?"):
        print(message)

anyio.run(main)
```

**Note:** This step is self-contained — it does not depend on anything saved in `ep02/agent.py`. No import-line callout is needed here (compare to Ep01's rule 2a); there's no shared file state to pull in yet.

---

## Main Build — `ep02/agent.py` (write these in order, into the same file)

### Step 3 — Imports, prompt constant, and options
📄 agent.py — top of file
→ HTML slide 15

```python
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
```

### Step 4 — The run loop
📄 agent.py — continued
→ HTML slide 16

```python
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
```

**Recording note:** Run this file from inside `ep02/` (so `cwd="../"` correctly resolves to the repo root). If you retake this step, there's no shared `messages` list to reset — unlike Ep01, re-running this file from scratch is always safe. Nothing to reset between takes.

---

## Final File — the complete, authoritative version

📄 agent.py — FINAL
→ HTML slide 19

```python
"""
Claude Certified Developer -- Build-Along
Ep 02: Same agent as Ep01, rebuilt on the Claude Agent SDK.
Repo: claude-api-masterclass/ep02/agent.py
"""

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
```
