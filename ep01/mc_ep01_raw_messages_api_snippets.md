# Episode 01 — Code Snippets Companion
### `mc_ep01_raw_messages_api_snippets.md` — for use during recording, not for viewers

No narration, no callouts — just every runnable code block from the episode, in the exact order to paste it, each one tagged the same way as the HTML script (🧪 ipython / 📄 agent.py) with a pointer back to the matching slide. Read top to bottom while recording.

**Golden rule:** everything under "Main sequence" is **one continuous ipython session**. If you restart ipython for any reason, start over from Step 3 (the import line) — don't try to resume mid-sequence.

---

## Setup check (standalone — not part of the main sequence, run once, separately)
→ HTML slide 5

🧪 terminal, not saved
```bash
pip install anthropic ipython
export ANTHROPIC_API_KEY="your-key-here"
```

🧪 sanity check, not saved
```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(response.content[0].text)
```
👉 If this prints something, delete/close this — it does not go into `agent.py`.

---

## Main sequence — build `agent.py`, then switch to ipython

### Step 1 — 📄 agent.py (top of file)
→ HTML slide 6
```python
import anthropic

client = anthropic.Anthropic()

# a tiny stand-in "repo" — real file access comes later in the series
REPO_FILES = {
    "README.md": "# PR Review Agent\nDemo repo for this series.",
    "src/auth.py": "def check_token(token):\n    # TODO: never actually validates anything\n    return True",
    "src/utils.py": "def slugify(text):\n    return text.lower().replace(' ', '-')",
}

def read_repo_file(path):
    if path in REPO_FILES:
        return REPO_FILES[path]
    return f"Error: no file at '{path}' in this repo."
```

### Step 2 — 📄 agent.py (continued)
→ HTML slide 7
```python
tools = [
    {
        "name": "read_repo_file",
        "description": (
            "Read the full text contents of a single file from the demo "
            "repository, given its path relative to the repo root (e.g. "
            "'src/utils.py'). Use this whenever you need to see what a "
            "file actually contains before answering a question about it "
            "— do not guess at file contents you have not read."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root, e.g. 'src/utils.py'",
                }
            },
            "required": ["path"],
        },
    }
]
```
👉 Save `agent.py` now. Open a terminal, `cd` into `claude-api-masterclass/ep01`, confirm the venv is active, then start a fresh `ipython` session for everything below.

### Step 3 — 🧪 ipython (run first, every session)
→ HTML slide 8
```python
from agent import client, tools, read_repo_file
```

### Step 4 — 🧪 ipython (Turn One)
→ HTML slide 8
```python
messages = [
    {"role": "user", "content": "What does src/auth.py do?"}
]

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print(response.stop_reason)   # "tool_use"
print(response.content)       # a tool_use block, not text!
```

### Step 5 — 🧪 ipython (the two rules)
→ HTML slide 10
```python
messages.append({"role": "assistant", "content": response.content})

tool_use_block = response.content[0]
result_text = read_repo_file(tool_use_block.input["path"])

messages.append({
    "role": "user",
    "content": [{
        "type": "tool_result",
        "tool_use_id": tool_use_block.id,
        "content": result_text,
    }],
})
```

### Step 6 — 🧪 ipython (Turn Two)
→ HTML slide 11
```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    tools=tools,
    messages=messages,
)

print(response.stop_reason)          # "end_turn"
print(response.content[0].text)      # the real answer, finally
```

### ⏭ Skip — HTML slide 12 ("From Two Turns To A Loop")
That slide is shape-only illustration (`model=...` is a placeholder, not real code). Don't paste it into ipython — narrate over it instead, then move straight to Step 7.

### Step 7 — 🧪 ipython (assembling run_agent — defines the function; optional to also call it here)
→ HTML slide 14
```python
def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "read_repo_file":
                    result_text = read_repo_file(block.input["path"])
                else:
                    result_text = f"Error: unknown tool '{block.name}'"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        if response.stop_reason in ("max_tokens", "stop_sequence"):
            return f"[Stopped early: {response.stop_reason}]"

        if response.stop_reason == "refusal":
            return "[Claude declined to answer this one.]"

        return f"[Unhandled stop_reason: {response.stop_reason}]"
```
Optional live demo call, same session:
```python
print(run_agent("What does src/auth.py do, and does it look finished to you?"))
```

### Step 8 — 📄 agent.py — FINAL (replace the whole file with this)
→ HTML slide 15
```python
import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY automatically

# --- a tiny stand-in "repo" — real file access comes later in the series ---
REPO_FILES = {
    "README.md": "# PR Review Agent\nDemo repo for this series.",
    "src/auth.py": "def check_token(token):\n    # TODO: never actually validates anything\n    return True",
    "src/utils.py": "def slugify(text):\n    return text.lower().replace(' ', '-')",
}

def read_repo_file(path):
    if path in REPO_FILES:
        return REPO_FILES[path]
    return f"Error: no file at '{path}' in this repo."

# --- the one tool Claude can see ---
tools = [
    {
        "name": "read_repo_file",
        "description": (
            "Read the full text contents of a single file from the demo "
            "repository, given its path relative to the repo root (e.g. "
            "'src/utils.py'). Use this whenever you need to see what a "
            "file actually contains before answering a question about it "
            "— do not guess at file contents you have not read."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root, e.g. 'src/utils.py'",
                }
            },
            "required": ["path"],
        },
    }
]

# --- the agentic loop ---
def run_agent(user_message):
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            tools=tools,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if block.name == "read_repo_file":
                    result_text = read_repo_file(block.input["path"])
                else:
                    result_text = f"Error: unknown tool '{block.name}'"

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

            messages.append({"role": "user", "content": tool_results})
            continue

        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        if response.stop_reason in ("max_tokens", "stop_sequence"):
            return f"[Stopped early: {response.stop_reason}]"

        if response.stop_reason == "refusal":
            return "[Claude declined to answer this one.]"

        return f"[Unhandled stop_reason: {response.stop_reason}]"


if __name__ == "__main__":
    print(run_agent("What does src/auth.py do, and does it look finished to you?"))
```
👉 Exit ipython. Save this over the whole file. Run `python agent.py` from the terminal — that's the real, final, standalone execution to close the episode on.
