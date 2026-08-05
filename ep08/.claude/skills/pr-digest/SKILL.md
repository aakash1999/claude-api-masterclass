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