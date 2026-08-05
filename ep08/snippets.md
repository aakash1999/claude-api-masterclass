# Ep08 — Skills: Reusable Agent Capabilities — Snippets Companion

---

## Main sequential session

### 1 — 📄 .claude/skills/pr-digest/SKILL.md
→ HTML slide 10, "Writing pr-digest/SKILL.md"

```markdown
---
name: pr-digest
description: Turn an already-reviewed PR into a short, plain-English
  digest a human can read without opening the PR -- 3-5 sentences,
  not a list of findings. Use this when someone asks for a summary,
  a digest, a recap, or "what happened in this review" for a PR
  that this project's PR Review Agent has already reviewed in the
  current conversation.
license: Apache-2.0
allowed-tools: Read
---

You are writing a digest for a human who will not open the PR
themselves.

1. Use only what's already in this conversation: every
   submit_finding result and the publish_review comment for this
   PR. Do not re-fetch the PR and do not re-run the review.
2. Write 3-5 sentences. Lead with the verdict, then the one or two
   things that actually matter. This is not a bullet-point dump.
3. Never invent a finding that wasn't actually submitted. Zero
   findings still deserves a one-line digest.
4. End with exactly one line: a count by severity, e.g.
   "1 blocking, 0 warning, 2 nit."
```

### 2 — 📄 .claude/skills/changelog-entry/SKILL.md
→ HTML slide 12, "Writing changelog-entry/SKILL.md"

```markdown
---
name: changelog-entry
description: Draft exactly one Keep a Changelog-style entry from a
  PR digest that already exists in this conversation. Use this
  when someone asks for a changelog line, a release note, or a
  "changelog entry" for a PR that has already been summarized
  (typically by the pr-digest skill) earlier in the conversation.
license: Apache-2.0
allowed-tools: Read
---

You are drafting exactly one changelog entry, Keep a Changelog
format (keepachangelog.com): a category heading -- Added, Changed,
Fixed, Removed, or Security -- and one bullet, written for END
USERS of the product, not developers reading this repo. No file
paths, no severities, no internal finding language.

1. Use the digest already produced in this conversation as your
   only source. Do not go re-read the PR and do not re-run the
   review.
2. Pick the category that matches what the PR actually does, not
   the category a reviewer's severity label suggests -- "blocking"
   is about review urgency, it has nothing to do with the
   changelog's Added/Changed/Fixed axis.
3. One bullet, one sentence, plain language a user of the product
   would understand -- not a user of this codebase.
4. If the digest doesn't contain enough to write a genuinely
   user-facing line -- say, an internal refactor with no visible
   change -- say that instead of inventing user impact.
```

### 3 — 📄 agent.py — the Skills addition
→ HTML slide 14, "Wiring Skills Into agent.py"

Inside `build_options()`, sitting right after `allowed_tools=[...]`:

```python
skills=["pr-digest", "changelog-entry"],
# Ep06 — without "project" in this list, CLAUDE.md is never loaded.
# Also required for Skill discovery.
setting_sources=["project"],
# Ep08 -- headless run, nobody's at a terminal to click "approve."
permission_mode="dontAsk",
```

### 4 — 🧪 terminal — running the chain
→ HTML slide 17, "Running The Chain On PR #143"

Run from inside `ep08/`. Resumes the Episode 7 session for PR #143 — no
`fresh=True`, so `get_session_id(143)` finds the prior session, and its
transcript already has `publish_review` in it from last episode's run.

```bash
python agent.py 143 "Give me a short digest of this PR's review, then draft one changelog entry from it."
```

---

## Non-runnable illustration blocks (skipped)

⏭ skip — illustrative only, see HTML slide 8 ("Anatomy Of A SKILL.md
File"). The annotated `deploy-check` example shown there exists purely to
walk through frontmatter fields (`argument-hint`, `model`, `context: fork`,
etc.) — it is not part of this project and was never meant to be pasted
anywhere.

⏭ skip — reference only, see HTML slide 16 ("The Gotcha, Part 2 — Don't
Add 'Skill' To allowed_tools Yourself"). The `types.py` docstring excerpt
and the printed effective-`allowed_tools` output shown there are quoted
directly from the installed `claude-agent-sdk` 0.2.128 package to prove a
claim on camera — they're third-party SDK internals, not this project's
code, and there's nothing here to paste into `ep08/`.

⏭ skip — illustrative only, see HTML slide 18 ("What You'd See On
Screen"). The terminal transcript shown is a representative example, not
a literal script to paste — the model's actual wording will vary. Run the
command in step 4 above for real instead.

---

## Final Files (complete, paste-ready — the source of truth)

### 5 — 📄 .claude/skills/pr-digest/SKILL.md — FINAL
→ HTML slide 19, "Final File — pr-digest/SKILL.md"

```markdown
---
name: pr-digest
description: Turn an already-reviewed PR into a short, plain-English
  digest a human can read without opening the PR -- 3-5 sentences,
  not a list of findings. Use this when someone asks for a summary,
  a digest, a recap, or "what happened in this review" for a PR
  that this project's PR Review Agent has already reviewed in the
  current conversation.
license: Apache-2.0
allowed-tools: Read
---

You are writing a digest for a human who will not open the PR
themselves.

1. Use only what's already in this conversation: every
   submit_finding result and the publish_review comment for this
   PR. Do not re-fetch the PR and do not re-run the review -- the
   findings already exist, your job is only to translate them into
   plain English.
2. Write 3-5 sentences. Lead with the verdict -- does this PR look
   safe to merge or not -- then the one or two things that actually
   matter. Anything genuinely minor gets, at most, a passing clause.
   This is not a bullet-point dump of every finding.
3. Never invent a finding that wasn't actually submitted. If there
   were zero findings, say that plainly -- a clean PR still
   deserves a one-line digest.
4. End with exactly one line: a count by severity, e.g.
   "1 blocking, 0 warning, 2 nit."
```

### 6 — 📄 .claude/skills/changelog-entry/SKILL.md — FINAL
→ HTML slide 20, "Final File — changelog-entry/SKILL.md"

```markdown
---
name: changelog-entry
description: Draft exactly one Keep a Changelog-style entry from a
  PR digest that already exists in this conversation. Use this
  when someone asks for a changelog line, a release note, or a
  "changelog entry" for a PR that has already been summarized
  (typically by the pr-digest skill) earlier in the conversation.
license: Apache-2.0
allowed-tools: Read
---

You are drafting exactly one changelog entry, Keep a Changelog
format (keepachangelog.com): a category heading -- Added, Changed,
Fixed, Removed, or Security -- and one bullet, written for END
USERS of the product, not developers reading this repo. No file
paths, no severities, no internal finding language.

1. Use the digest already produced in this conversation (by the
   pr-digest skill, or whatever summary of the PR already exists)
   as your only source. Do not go re-read the PR and do not re-run
   the review.
2. Pick the category that matches what the PR actually does, not
   the category a reviewer's severity label would suggest --
   "blocking" in a review is about review urgency, it has nothing
   to do with the changelog's Added/Changed/Fixed axis.
3. One bullet, one sentence, plain language a user of the product
   would understand -- not a user of this codebase.
4. If the digest doesn't contain enough information to write a
   genuinely user-facing line -- for example, it's an internal
   refactor with no user-visible change -- say that instead of
   inventing user impact that isn't there.
```

### 7 — 📄 agent.py — FINAL
→ HTML slide 21, "Final File — agent.py"

```python
"""PR & Repo Review Agent — Episode 08: reusable Skills, chained.

Run this from inside `ep08/`. Two reasons, both load-bearing:
  1. CLAUDE.md is discovered from the working directory upward.
  2. Skills are discovered the same way — from `.claude/skills/` in the
     working directory and every parent up to the repository root.
Session transcripts are also keyed by working directory, so `resume` from a
different cwd silently starts a brand new conversation.

What changed since Ep07: two Skills now live on disk — `pr-digest` and
`changelog-entry` (see `.claude/skills/`). Neither is wired into the review
flow itself; they're on-demand, chained on top of a review that's already
been published. This file's only change is `build_options()` turning them on.
"""

import asyncio
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
)

from hooks import (
    block_dangerous_bash,
    log_precompact,
    process_pr_fetch_result,
    require_evidence,
)
from session_index import get_session_id, remember_session
from subagents import REVIEW_AGENTS
from tools import (
    check_docstrings,
    fetch_pr_metadata,
    publish_review,
    reset_findings,
    submit_finding,
)

pr_tools = create_sdk_mcp_server(
    name="pr_tools",
    version="1.0.0",
    tools=[check_docstrings, fetch_pr_metadata, submit_finding, publish_review],
)


def build_options(
    resume_id: str | None = None,
    fork: bool = False,
) -> ClaudeAgentOptions:
    """Everything Ep01-07 built, plus this episode's two Skills."""
    return ClaudeAgentOptions(
        mcp_servers={"pr_tools": pr_tools},
        agents=REVIEW_AGENTS,
        allowed_tools=[
            "Agent",
            "Read",
            "Grep",
            "Glob",
            "mcp__pr_tools__check_docstrings",
            "mcp__pr_tools__fetch_pr_metadata",
            "mcp__pr_tools__submit_finding",
            "mcp__pr_tools__publish_review",
        ],
        # Ep08 -- the single place to turn Skills on. Checked directly
        # against installed claude-agent-sdk 0.2.128 source (types.py,
        # subprocess_cli.py): setting this ALSO grants the tool access each
        # Skill needs -- it appends Skill(pr-digest) and Skill(changelog-entry)
        # to the *effective* allowed_tools sent to the CLI, on top of the
        # list above. Do NOT also add "Skill" to allowed_tools yourself --
        # the SDK source marks passing "Skill" there directly as deprecated
        # now that this option exists to do it for you.
        skills=["pr-digest", "changelog-entry"],
        # Ep06 — without "project" in this list, CLAUDE.md is never loaded.
        # Also required for Skill discovery. Confirmed in source: the SDK
        # only *defaults* setting_sources to ["user", "project"] when it's
        # unset -- since we set it ourselves, our explicit list is left alone.
        setting_sources=["project"],
        # Ep08 -- this review runs headless; nobody's at a terminal to click
        # "approve." "dontAsk" denies anything outside allowed_tools instead
        # of prompting for it (and prompting for it here would just hang).
        permission_mode="dontAsk",
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[block_dangerous_bash]),
            ],
            "PostToolUse": [
                HookMatcher(
                    matcher="mcp__pr_tools__fetch_pr_metadata",
                    hooks=[process_pr_fetch_result],
                ),
            ],
            "Stop": [HookMatcher(hooks=[require_evidence])],
            "PreCompact": [HookMatcher(hooks=[log_precompact])],
        },
        # Ep06 — resume is None on a first run, which the SDK reads as "fresh".
        resume=resume_id,
        fork_session=fork,
    )


async def review_pr(
    pr_number: int,
    prompt: str,
    *,
    fresh: bool = False,
    fork: bool = False,
) -> str | None:
    """Review a PR, resuming the previous session for that PR when we have one.

    Also how this episode's two Skills get exercised -- a `prompt` that just
    asks for a digest and a changelog entry, resumed against a PR session
    that already has a published review sitting in its transcript, needs no
    change here at all. `reset_findings()` clears the module-level
    `_FINDINGS` list either way -- that list is a call-scoped cache purely
    for `publish_review` to build a comment from *this run's* findings; it
    is not where the digest Skill reads from. The digest reads the actual
    resumed conversation transcript, which the SDK reloads independently of
    anything in our own Python process.
    """
    prior = None if fresh else get_session_id(pr_number)
    if prior:
        print(f"-> resuming session {prior[:8]} for PR #{pr_number}")
    else:
        print(f"-> new session for PR #{pr_number}")

    reset_findings()

    session_id = None
    try:
        async for message in query(prompt=prompt, options=build_options(prior, fork)):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                session_id = message.session_id
    except Exception as error:
        print(f"[error] {error}")

    if session_id is None:
        return None

    if fork:
        print(f"-> forked into {session_id[:8]} (original left intact)")
    else:
        remember_session(pr_number, session_id)
        print(f"-> remembered session {session_id[:8]} for PR #{pr_number}")

    return session_id


async def main() -> None:
    pr_number = int(sys.argv[1]) if len(sys.argv) > 1 else 143
    prompt = (
        sys.argv[2]
        if len(sys.argv) > 2
        else f"Review PR #{pr_number}. Fan out to both reviewers, then post one comment."
    )
    await review_pr(pr_number, prompt)


if __name__ == "__main__":
    asyncio.run(main())
```

---

*Snippets companion — Ep08, Claude Certified Developer, The Build-Along Course.*
