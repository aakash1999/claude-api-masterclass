import re
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# MCP-over-stdio requires each JSON-RPC response to be on its own line and
# flushed before the next one. Python's stdout defaults to fully-buffered
# when piped (which is exactly how this server runs when launched by a
# client), so without this reconfigure, the responses can sit in the
# buffer and never reach the client. Line buffering flushes on every \n.
sys.stdout.reconfigure(line_buffering=True)

mcp = FastMCP("repo_facts")


@mcp.tool()
def count_todos(directory: str = ".") -> str:
    """Count TODO and FIXME comments across every .py file under
    `directory`. Returns a plain-text report: how many were found, and
    each one's file, line number, and the line itself.
    """
    hits = []
    for path in sorted(Path(directory).rglob("*.py")):
        for lineno, line in enumerate(
            path.read_text(errors="ignore").splitlines(), start=1
        ):
            if re.search(r"#\s*(TODO|FIXME)\b", line):
                hits.append(f"{path}:{lineno}  {line.strip()}")
    if not hits:
        return "No TODO or FIXME comments found."
    return f"{len(hits)} found:\n" + "\n".join(hits)


if __name__ == "__main__":
    mcp.run()  # stdio by default -- matches "type": "stdio" in .mcp.json
