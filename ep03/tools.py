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

review_tools = create_sdk_mcp_server(
    name="review-tools",
    version="1.0.0",
    tools=[check_docstring_coverage],
)

#mcp__{server_name}__{tool_name} -> mcp__review-tools__check_docstring_coverage