"""
ep07/schemas.py
The shape of one review finding, plus the validation that actually enforces it.

Why this file exists: the raw Messages API has a real, GA feature called
"strict tool use" (`strict: true` on a tool definition) that guarantees
Claude's tool input matches a JSON Schema exactly, via grammar-constrained
sampling -- no retries needed for shape violations. It used to sit behind
the `structured-outputs-2025-11-13` beta header; that requirement is gone.

BUT -- and this is the whole reason this file has a validate_finding()
function and not just a schema -- `strict` is a field on a raw Messages
API tool DEFINITION. Checked directly against installed claude-agent-sdk
0.2.128 source: the SDK's own `SdkMcpTool` dataclass (what the `@tool`
decorator builds -- the exact style every custom tool in this project has
used since Episode 03) has no `strict` field, and `create_sdk_mcp_server()`
never forwards one onto the MCP tool it registers. So on this tool path,
that hard guarantee doesn't exist yet. The schema below still helps --
Claude reads it and is guided by it -- but "guided by" is not "guaranteed
by" until the SDK wires that flag through. validate_finding() is what
actually enforces the rules, today.
"""

from typing import Any

ALLOWED_SEVERITIES = ("blocking", "warning", "nit")

# Written the way a *strict* tool definition would want it: every property
# listed in "required" -- strict mode has no concept of an optional
# property, "optional" is expressed by allowing null instead -- and
# additionalProperties: False so nothing sneaks in unannounced. We don't
# have the enforcement yet on this tool path (see module docstring), but
# writing it this way now means this exact dict drops onto a raw-API
# strict tool definition later with zero changes.
FINDING_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "file_path": {
            "type": "string",
            "description": "Path to the file this finding applies to, relative to repo root.",
        },
        "line": {
            "type": "integer",
            "description": "The line number this finding applies to.",
        },
        "severity": {
            "type": "string",
            "enum": list(ALLOWED_SEVERITIES),
            "description": "Exactly one of blocking, warning, or nit. Never invent a fourth label.",
        },
        "message": {
            "type": "string",
            "description": "One or two sentences on the issue. Be specific, not generic.",
        },
        "suggested_fix": {
            "type": ["string", "null"],
            "description": (
                "A concrete code-level fix, if you're confident in one. "
                "Pass null -- not a guess, not a placeholder -- if you aren't."
            ),
        },
    },
    "required": ["file_path", "line", "severity", "message", "suggested_fix"],
    "additionalProperties": False,
}


def validate_finding(args: dict[str, Any]) -> list[str]:
    """Check one finding against the rules the schema above can describe
    but not (yet) enforce on this tool path. Returns a list of specific
    problems -- an empty list means the finding is good to record.

    Every message here is written to go straight back to Claude as a tool
    result, so each one says exactly what's wrong, not just that something
    is wrong. A vague "invalid input" can't be corrected; a precise one can.
    """
    errors: list[str] = []

    file_path = args.get("file_path")
    if not isinstance(file_path, str) or not file_path.strip():
        errors.append("file_path must be a non-empty string.")

    line = args.get("line")
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
        errors.append("line must be a positive integer (line numbers start at 1).")

    severity = args.get("severity")
    if severity not in ALLOWED_SEVERITIES:
        errors.append(
            f"severity must be exactly one of {list(ALLOWED_SEVERITIES)} -- "
            f"got {severity!r}. Do not invent a new label."
        )

    message = args.get("message")
    if not isinstance(message, str) or not message.strip():
        errors.append("message must be a non-empty string.")

    if "suggested_fix" not in args:
        errors.append(
            "suggested_fix is required -- pass null if you don't have a "
            "confident fix, do not omit the field."
        )
    else:
        suggested_fix = args["suggested_fix"]
        if suggested_fix is not None and not isinstance(suggested_fix, str):
            errors.append("suggested_fix must be a string or null.")

    return errors