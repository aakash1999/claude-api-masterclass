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