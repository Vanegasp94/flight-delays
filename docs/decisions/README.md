# Architecture decision records

Each significant technical decision gets one short Markdown file in this folder,
so the reasoning is still available later.

## How to add one

1. Copy [`0000-template.md`](0000-template.md) to `NNNN-short-title.md`, using
   the next free four-digit number (`0001-...`, `0002-...`).
2. Fill in every section. Keep it to about a page.
3. Commit it together with the change it describes, or before it.

## Format

| Section | What goes in it |
|---|---|
| **Status** | `Proposed`, `Accepted`, `Superseded by NNNN` or `Rejected`, with the date |
| **Context** | The situation and constraints that force a decision. Facts, not the solution |
| **Decision** | What was decided, stated plainly in the active voice |
| **Alternatives considered** | The other options and why each was not chosen |
| **Consequences** | What becomes easier, what becomes harder, and any follow-up work |

## Rules

- Records are not edited after they are accepted, apart from the status line.
  A changed decision gets a new record that supersedes the old one.
- Write what is known at the time. Mark assumptions as assumptions.
