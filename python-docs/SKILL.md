---
name: python-docs
description: >
  Audit Python source code for missing or incomplete docstrings and fill them in.
  Trigger when the user says "add docstrings", "document this", "write docs for this",
  or "check my docstrings". Do NOT trigger for routine Python code writing — pattern
  recognition from existing code handles that. This skill is for a deliberate documentation
  pass over code the user is satisfied with.
---

# Python Docs Skill

## What This Skill Does

A focused docstring audit pass. Read the source, find gaps, fill them.
Nothing else unless the user explicitly asks for MkDocs setup.

## Docstring Standard — Google Style

```python
def submit_workflow(name: str, namespace: str, dry_run: bool = False) -> dict:
    """Submit a workflow template to the target cluster.

    One-paragraph summary of what this does and why, not just what
    the parameters are.

    Args:
        name: Workflow template name as registered in the cluster.
        namespace: Kubernetes namespace to submit into.
        dry_run: If True, validate only — do not submit. Defaults to False.

    Returns:
        The created Workflow resource dict from the Argo API response.

    Raises:
        WorkflowNotFoundError: If `name` does not match a registered template.

    Example:
        >>> result = submit_workflow("deploy-prod", "production")
        >>> print(result["metadata"]["name"])
        deploy-prod-x4k2z
    """
```

## Required Sections by Symbol

| Symbol | Required |
|---|---|
| Module | One-paragraph summary at top of file |
| Class | Summary + `Attributes:` for public attrs |
| `__init__` | `Args:` only |
| Public method / function | Summary + `Args:` + `Returns:` + `Raises:` if applicable |
| Property | One-liner |
| Exception | Summary + when raised |

Skip `Args:` / `Returns:` only when type annotations make it completely self-evident.

## Audit Process

1. Read all `.py` files in scope
2. Identify: missing docstrings, one-liners that need expansion, stale docs that don't match current signatures
3. Fill gaps — write docstrings in place, don't just describe what's missing
4. Note any function names or signatures that are unclear enough that a docstring can't save them — flag for rename

## What Not To Do

- Don't write `.md` files describing what code does — that goes stale
- Don't scaffold MkDocs unless explicitly asked
- Don't add docstrings to private functions (`_name`) unless they're complex enough to warrant it

## If User Asks for MkDocs Too

```bash
pip install mkdocs-material mkdocstrings[python] mkdocs-gen-files mkdocs-literate-nav
```

- GitHub repo → GitHub Actions + `mkdocs gh-deploy` → GitHub Pages


See user for preferred hosting target before scaffolding.