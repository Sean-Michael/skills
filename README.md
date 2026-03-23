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

This was born out of a necessity to instill some semblence of security best practice when creating web applications. Honestly anything that is exposed to the public internet should be considered 'production' just in some sense so that it's treated with the respect that it deserves to be properly secured. Even if the data behind is is inconsequential, I don't want to leave something to chance like forgetting I stored some personal info or left a backdoor open. 

Claude already has a lot of training data on this topic but I feel that sometimes I have to specifically prompt a bit to explicitly the basics. Obvioulsy the model is optimizing for a quick resolution of a request like 'build me a fastapi application' and not exactly diving deep into rate limiting, auth models, etc. 

So my hope is just by simply invoking this skill and these topics getting placed in the context, all of this will surface and better the app output.

