---
name: obsidian-cli
description: >
  Interact with an Obsidian vault using the official Obsidian CLI. Trigger
  when asked to read, write, search, or organize vault content, capture a
  decision or gotcha, log to a daily note, or reorganize notes. Also trigger
  on "make a note of that", "log that", "update my vault".
---

# Obsidian CLI

Always use the CLI over direct `.md` file edits — it runs through Obsidian's
runtime so `move` updates links, `create` applies templates, `property:set`
writes valid frontmatter.

Run `obsidian help` to discover commands. Run `obsidian help <command>` for params.

**`file=<n>`** resolves like a wikilink — no path or extension needed.  
**`path=<path>`** requires exact path from vault root.

---

## Vault Structure (PARA)

Organize vaults using PARA:

```
Vault/
├── Projects/    # active work with a defined end state
├── Areas/       # ongoing responsibilities, no end date
├── Resources/   # reference material, things learned
├── Archive/     # completed or dead projects
├── Daily Notes/
├── Templates/
└── Attachments/
```

**Projects vs Areas:** Projects have a finish line and move to Archive when
done. Areas are permanent responsibilities that never "end".

Meeting notes live inside the relevant project folder, not a global folder.

---

## Project Note Structure

Path: `Projects/<Project>/<Project>.md`

```markdown
---
project: <name>
status: active
updated: <YYYY-MM-DD>
tags: [project]
---

# <Project Name>

## What & Why
What this is and why it exists.

## Current Status
Where things are right now.

## Decisions & Tradeoffs
- **<decision>** — why, and what was rejected

## Gotchas & Lessons
- Things that bit you or future-you needs to know

## Open Questions
- Unresolved things
```

---

## Daily Note

Append tasks and quick references rather than creating new notes for small things:

```bash
obsidian daily:append content="- [ ] Task here"
obsidian daily:append content="- [[Project]] — note for references section"
```

---

## PKM Conventions

**Wikilink liberally.** Any time a known project, person, or concept appears
in a note, link it: `[[Project Name]]`, `[[Person]]`.

**Check before creating.** A note may already exist:
```bash
obsidian search query="<topic>" limit=5
```

**Shallow structure.** No nesting beyond `Projects/<Project>/` except a
`Meeting Notes/` subfolder per project if needed.

**Small tag set.** Stick to: `project`, `area`, `resource`, `decision`,
`gotcha`, `question`. Don't invent tags without a clear reason.

**Archiving.** Move don't delete:
```bash
obsidian move file="<Project>" to="Archive/"
obsidian property:set name=status value=done file="<Project>"
```

---

## When "Make a Note of That"

1. Identify type:
   - Decision/tradeoff/gotcha → append to project note
   - Task → `obsidian daily:append`
   - Meeting → `Projects/<Project>/Meeting Notes/<date> <topic>.md`
   - Reference → `Resources/<topic>.md`
2. Check the target exists before appending
3. Create if missing, append if it exists
4. Update `updated` frontmatter with today's date
5. Confirm what was written and where

