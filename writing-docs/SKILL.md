---
name: writing-docs
description: >
  Write, restructure, or review prose documentation: READMEs, tutorials,
  how-to guides, reference pages, docs sites. Trigger on "write docs",
  "document this project", "write a README", "write a tutorial/guide",
  "clean up our docs", "docs overhaul". Not for docstrings (use python-docs).
---

# Writing Docs

Structure is Diátaxis. You know it. Apply it silently; don't lecture the user about it.

## Classify before writing

Each page answers one pair: action or cognition? Study or work?

|               | Study (acquire) | Work (apply) |
|---------------|-----------------|--------------|
| **Action**    | Tutorial        | How-to guide |
| **Cognition** | Explanation     | Reference    |

If a page answers two, split it and link between them. The most common defect is
blur between adjacent types: tutorials that explain, reference that instructs,
how-tos that teach.

## Per-type nudges

- **Tutorial**: one path, no alternatives. Every step produces visible output
  ("You should see…"). It must work end to end on a clean setup, so run it.
- **How-to**: the title is the goal ("How to rotate API keys"). Assume competence.
  Branching is fine ("If X, do Y"). Usable beats complete.
- **Reference**: mirror the code's structure and give every entry the same shape.
  Describe only. This is the one place to be exhaustive. Generate it from source
  where possible.
- **Explanation**: why, history, trade-offs, alternatives. Opinion is allowed.
  Frame it as "About X".

## README

A README is a signpost, not a fifth type. It's the one page allowed to mix types,
and only in small doses:

1. What the project is and why it exists, in one paragraph with no marketing.
   This is a slice of explanation.
2. A quickstart that runs in as few commands as possible. This is a minimal tutorial,
   one path with its expected output.
3. Links to the rest of the docs.

When a section grows past a screen, it belongs on its own page of the right type.
Small projects can keep reference (a flags table, config options) inline.

## Standards

- Every example is copy-pasteable and was actually run. Show the expected output.
- Headings are the outline. A reader skimming only the headings should get the gist.
- Repeat a prerequisite inline rather than send the reader off mid-task. Link for
  everything else.
- Never put information only in an image; agents and search can't read it.
- Stale docs are worse than missing docs. Delete what's wrong.
- Don't scaffold empty Tutorial/How-to/Reference/Explanation sections. Structure
  grows from real content.
- Follow the project's docs style guide if one exists.

## Code snippets

Prefer real code from the repo over invented examples. Trim a snippet to the lines
that matter, cite where it came from (`path:line` or a link), and annotate only the
lines a reader would trip on. Invented examples must still run.

## Write like a person

Write for a human reading it in a hurry. Cut these Claude tics:

- Throat-clearing intros ("In this guide, we'll explore…") and recap outros.
  A tutorial may open with a single sentence that states what the reader will build.
- Filler words: comprehensive, robust, seamless, powerful, leverage, delve,
  "it's important to note".
- Bullets for things that read better as a sentence. Bold scattered through
  paragraphs. Emoji in headings.
- Em-dash chains and "not just X, but Y" constructions.
- Hedging on facts. If it's true, state it. If you're unsure, check.

Plain, specific, and short beats polished.
