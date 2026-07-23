
## STANDALONE SETUP (not part of the sequential build)

### Setup 1 — sanity-check the ast approach
🧪 sanity check, not saved
→ HTML slide 8

```python
import ast

source = open("../ep01/agent.py").read()
tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        print(node.name, ast.get_docstring(node) is None)
```

Run from repo root. This is throwaway — proves the ast idea works before any SDK code gets written. Not saved anywhere.

---

## SEQUENTIAL BUILD — tools.py

### Step 1 — imports + REPO_ROOT
📄 tools.py — top of file
→ HTML slide 9

```python
"""
Claude Certified Developer -- Build-Along
Ep 03: Custom tool -- docstring coverage checker.
Repo: claude-api-masterclass/ep03/tools.py
"""

import ast
from pathlib import Path
from typing import Annotated, Any

from claude_agent_sdk import tool, create_sdk_mcp_server, ToolAnnotations

REPO_ROOT = Path(__file__).resolve().parent.parent  # .../claude-api-masterclass
```

### Step 2 — the @tool decorator + schema
📄 tools.py — continued
→ HTML slide 10

```python
@tool(
    "check_docstring_coverage",
    "Parse a Python file with the ast module and report every function and "
    "class definition missing a docstring, with line numbers. More reliable "
    "than grepping for 'def' -- it understands Python structure, not just "
    "text patterns. Use this before approving a PR that touches public "
    "functions or classes. Optionally pass include_private=true to also "
    "flag private methods and functions (leading underscore) -- by default "
    "they're skipped, since they're usually self-explanatory.",
    {
        "file_path": Annotated[
            str, "Path to the Python file to check, relative to the repo root."
        ],
    },
    annotations=ToolAnnotations(readOnlyHint=True),
)
```

⏭ **Note (HTML slide 11):** fact-check callout on `Annotated` and the required-fields rule — no new code, narration only. Skip in this file.

### Step 3 — the handler
📄 tools.py — continued
→ HTML slide 12

```python
async def check_docstring_coverage(args: dict[str, Any]) -> dict[str, Any]:
    include_private = args.get("include_private", False)  # optional -- not in schema, so .get()

    full_path = REPO_ROOT / args["file_path"]
    try:
        source = full_path.read_text()
    except FileNotFoundError:
        return {
            "content": [{"type": "text", "text": f"No file at {args['file_path']}"}],
            "is_error": True,
        }

    tree = ast.parse(source)
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not include_private and node.name.startswith("_"):
                continue
            if ast.get_docstring(node) is None:
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                missing.append(f"line {node.lineno}: {kind} '{node.name}'")

    if not missing:
        report = f"{args['file_path']}: every function and class has a docstring."
    else:
        report = (
            f"{args['file_path']}: {len(missing)} missing docstring(s)\n"
            + "\n".join(missing)
        )

    return {"content": [{"type": "text", "text": report}]}
```

⏭ **Note (HTML slide 13):** cwd gotcha callout — no new code, narration only. Skip in this file.

### Step 4 — sanity-check the handler directly (bypass Claude)
🧪 working it out — depends on tools.py already saved through Step 3
→ HTML slide 14

```python
import asyncio
from tools import check_docstring_coverage

result = asyncio.run(
    check_docstring_coverage.handler({"file_path": "ep01/agent.py"})
)
print(result["content"][0]["text"])
```

Run from repo root, with `ep03/tools.py` already saved. Expected output:
```
ep01/agent.py: 2 missing docstring(s)
line 10: function 'read_repo_file'
line 28: function 'run'
```

### Step 5 — wrap in the MCP server
📄 tools.py — bottom of file
→ HTML slide 15

```python
review_tools = create_sdk_mcp_server(
    name="review-tools",
    version="1.0.0",
    tools=[check_docstring_coverage],
)
```

---

## SEQUENTIAL BUILD — agent.py

### Step 6 — imports, prompt, options
📄 agent.py — top of file
→ HTML slide 16

```python
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
```

### Step 7 — the run loop
📄 agent.py — continued
→ HTML slide 17

```python
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
```

**Recording note:** run this file from inside `ep03/` (`cd ep03 && python agent.py`). There's no shared `messages` list to reset between takes — unlike Episode 01, `query()` manages history internally, so re-running from scratch is always safe.

### Step 8 — run it live
🧪 terminal, not saved
→ HTML slide 18

```bash
cd ep03
python agent.py
```

Expected shape (numbers are illustrative, not benchmarks — yours will vary):
```
[tool call] mcp__review-tools__check_docstring_coverage({'file_path': 'ep01/agent.py'})
[tool call] mcp__review-tools__check_docstring_coverage({'file_path': 'ep02/agent.py'})
ep01/agent.py is missing docstrings on read_repo_file and run --
worth adding before merge, since both are public entry points...

--- 2 turn(s) . $0.0031 . error=False ---
```

---

## FINAL FILES — the complete, authoritative versions

### 📄 tools.py — FINAL
→ HTML slide 20

```python
"""
Claude Certified Developer -- Build-Along
Ep 03: Custom tool -- docstring coverage checker.
Repo: claude-api-masterclass/ep03/tools.py
"""

import ast
from pathlib import Path
from typing import Annotated, Any

from claude_agent_sdk import tool, create_sdk_mcp_server, ToolAnnotations

REPO_ROOT = Path(__file__).resolve().parent.parent  # .../claude-api-masterclass


@tool(
    "check_docstring_coverage",
    "Parse a Python file with the ast module and report every function and "
    "class definition missing a docstring, with line numbers. More reliable "
    "than grepping for 'def' -- it understands Python structure, not just "
    "text patterns. Use this before approving a PR that touches public "
    "functions or classes. Optionally pass include_private=true to also "
    "flag private methods and functions (leading underscore) -- by default "
    "they're skipped, since they're usually self-explanatory.",
    {
        "file_path": Annotated[
            str, "Path to the Python file to check, relative to the repo root."
        ],
    },
    annotations=ToolAnnotations(readOnlyHint=True),
)
async def check_docstring_coverage(args: dict[str, Any]) -> dict[str, Any]:
    include_private = args.get("include_private", False)

    full_path = REPO_ROOT / args["file_path"]
    try:
        source = full_path.read_text()
    except FileNotFoundError:
        return {
            "content": [{"type": "text", "text": f"No file at {args['file_path']}"}],
            "is_error": True,
        }

    tree = ast.parse(source)
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not include_private and node.name.startswith("_"):
                continue
            if ast.get_docstring(node) is None:
                kind = "class" if isinstance(node, ast.ClassDef) else "function"
                missing.append(f"line {node.lineno}: {kind} '{node.name}'")

    if not missing:
        report = f"{args['file_path']}: every function and class has a docstring."
    else:
        report = (
            f"{args['file_path']}: {len(missing)} missing docstring(s)\n"
            + "\n".join(missing)
        )

    return {"content": [{"type": "text", "text": report}]}


review_tools = create_sdk_mcp_server(
    name="review-tools",
    version="1.0.0",
    tools=[check_docstring_coverage],
)
```

### 📄 agent.py — FINAL
→ HTML slide 21

```python
"""
Claude Certified Developer -- Build-Along
Ep 03: Wire the custom tool from tools.py into an agent.
Repo: claude-api-masterclass/ep03/agent.py
"""

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
    tools=[],
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
```

---

*Snippets file — Ep 03: Custom Tools — Claude Certified Developer, The Build-Along Course*
*All code in this file was executed against the installed `claude-agent-sdk` (v0.2.118) during fact-check: handler logic, schema generation (Annotated → description, required-keys behavior), and `ClaudeAgentOptions` construction all verified. The one step not live-tested is the actual `query()` call against the live API (no credentials in the fact-check environment) — the agentic loop mechanics themselves were already verified live in Episodes 01–02.*
