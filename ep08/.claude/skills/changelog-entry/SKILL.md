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