---
name: write-adr
description: Record an architecture decision record (ADR) in docs/adr from the template. Use when choosing between technical options, adding a significant dependency or external service, or changing architecture, data model, or public interfaces - or when the user asks for an ADR.
---

# Write an ADR

## Steps

1. **Pick the number.** List `docs/adr/`, take the highest `NNNN-` prefix, and add 1, zero-padded
   to 4 digits. `0000` is the template, so the first real ADR is `0001`.
2. **Name the file** `docs/adr/NNNN-<kebab-case-title>.md`, with the title as a short decision
   statement (e.g. `0003-use-postgres-for-event-storage.md`).
3. **Copy `docs/adr/0000-template.md`** to that path and fill in every section:
   - **Status**: `Proposed` (it becomes `Accepted` when the PR merges).
   - **Context**: the forces at play, such as requirements, constraints, and what prompted this now.
     Facts, not the solution.
   - **Decision**: one paragraph starting "We will ...".
   - **Consequences**: what gets easier, what gets harder, and follow-up work. Include the negatives.
   - **Alternatives considered**: at least two real options, each with why it lost.
4. **If this replaces an earlier ADR**, set the old one's status to `Superseded by NNNN` and link both ways.
5. **Show the user the draft** before finishing. Decisions need a human owner.
6. **Mention it** in the PR description under Changes.

## Rules

- One decision per ADR. Keep it under a page.
- Never edit the substance of an accepted ADR. Write a new one that supersedes it.
