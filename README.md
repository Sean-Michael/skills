# Skills

These are my mad programming skills for my llm friend named claude.

## Installation

I use this script to create symlinks to my home `.claude/skills` so I can access these system-wide.

```bash
git clone git@github.com:sean-michael/skills.git ~/skills
~/skills/install.sh
```

It's fully idempotent so re-running will add missing skills and not overwrite anything that I already have.

For example:

```bash
$ ./install.sh 
  up to date  grafana-dashboards
  linked      python-docs
  up to date  ui-ux
```

The symlinks ensure that the skills are always up to date with whatever the local git dir has.

## What's included

I've included skills for specific use cases borne from my experience developing platform infrastructure and DevOps automation tools.

### [grafana-dashboards](./grafana-dashboards/SKILL.md)

Everyone wants them but nobody wants to make them! Some people do, I don't really because I lack creativity in this visual sense. I know what's definitely *not* good though and I've attempted to distill some best practices of design and operational function here. 

The main goals are:

- provide a 5-second glance status check for an application
- never commit dashboards with broken queries

That's pretty much it. The LLM friend needs to be told that it should in fact validate that the queries it writes are actually possible to gather.

### [ui-ux](./ui-ux/SKILL.md)

In a similar vein as the grafana dashboards I often struggle to articulate the first time what a 'good' design or intuitive ui-ux experience looks like to an LLM agent. I definitely know what doesn't look good and after reading some blogs and design articles and whatnot I started to put together some key facets that could be transcribed in a skill.

These are pretty basic right now like, every user interaction should have a response, use color theory and give icons and colors semantic meaning, green is good, yellow is warning, red is error, etc.

### [python-docs](./python-docs/SKILL.md)

Sometimes I'll ask claude to write documentation for a codebase but this requires frequent updates as new features are added at the speed of whatever token rate anthropic is willing to give me.. so I figured we should probably act like adults and use `mkdocstrings` to make the code the source of truth.

The philosophy behind this skill is I don't want to bog-down the context of normal coding operations with a full trigger of the skill, instead I'll give some existing code and ask claude to create the docstrings. This way future claude sessions or agents will pickup on the patterns of docstrings in the context and intuitively continue it.

I also added some specifics on deploying with github pages using github actions. This is well documented online so I didn't feel the need to explicitly call out the implementation steps there.

### [production-grade](./production-grade/SKILL.md)
 
This was born out of a necessity to instill some semblance of security best practice when creating web applications. Honestly anything that is exposed to the public internet should be considered 'production' in some sense so that it's treated with the respect it deserves to be properly secured. Even if the data behind it is inconsequential, I don't want to leave something to chance like forgetting I stored some personal info or left a backdoor open.
 
Claude already has a lot of training data on this topic but sometimes I have to specifically prompt it to surface the basics. The model is optimizing for a quick resolution of a request like "build me a fastapi application" and not exactly diving deep into rate limiting, auth models, token storage, etc.
 
The skill encodes the things Claude consistently skips without being told — IDOR ownership checks, httpOnly cookies, middleware-layer rate limiting, single-use hashed reset tokens, structured logging with request IDs. The goal is that invoking the skill is enough: no more explicitly asking for each concern one by one.
 
### [obsidian](./obsidian/SKILL.md)
 
I really like Obsidian as a note taking and personal knowledge organization tool, but I am horrible at keeping it organized. I start off with good intentions and then slowly it gets derailed.
 
This skill is two things:
 
1. **CLI integration** — teaches Claude to use the official Obsidian CLI (shipped in v1.12.4) rather than reading and writing `.md` files directly. Going through the CLI means moves update internal links, creates apply templates, and frontmatter stays valid. The skill defers to `obsidian help` for command discovery so it stays current as the CLI evolves.
 
2. **PKM system** — codifies a PARA-based vault structure (Projects, Areas, Resources, Archive) and conventions for how notes should be created, linked, and maintained over time. The goal is self-documenting work: decisions, tradeoffs, gotchas, and project history captured as things happen rather than reconstructed later.
 
The skill is intentionally vault-agnostic so it can be used anywhere. Vault-specific context (project names, folder paths, daily note template) gets provided at prompt time.

