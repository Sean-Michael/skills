# Task Templates by Work Type

Copy-paste templates for common task types. Fill in the brackets.

## FastAPI Endpoint

```yaml
title: "Add [METHOD] /[path] endpoint for [purpose]"
description: |
  WHAT: Implement [endpoint] in [router file]. [Brief description of behavior.]
  WHY: Unblocks [feature/consumer]. Required for [milestone].
  FILES:
    - app/routers/[module].py
    - app/models/[model].py (if new schema)
    - app/schemas/[schema].py
    - tests/test_[module].py
  DONE_CRITERIA:
    - pytest tests/test_[module].py passes with [N] tests covering happy path + error cases
    - curl -X [METHOD] http://localhost:8000/[path] returns [expected response]
    - OpenAPI spec at /docs shows endpoint with correct schema
  NOTES: [Any auth requirements, dependencies on other services, edge cases]
risk: safe
estimated_tokens: low
dependencies: []
```

## HTMX Partial / Template

```yaml
title: "Add HTMX partial for [feature] in [template name]"
description: |
  WHAT: Create Jinja2 partial template for [feature]. Wire up hx-[trigger] on [element].
  WHY: [User-facing purpose]
  FILES:
    - app/templates/[feature].html (new partial)
    - app/templates/[parent].html (add include/trigger)
    - app/routers/[module].py (add partial endpoint if needed)
  DONE_CRITERIA:
    - Template renders without Jinja errors (python -c "render test")
    - hx-[trigger] attribute present on correct element
    - Endpoint returns 200 with text/html content-type
    - No inline JS (HTMX only)
  NOTES: [Design reference, component library used]
risk: safe
estimated_tokens: low
dependencies: []
```

## Test Coverage Gap

```yaml
title: "Add test coverage for [module/function]"
description: |
  WHAT: Write pytest tests for [module]. Current coverage: [X]%. Target: [Y]%.
  WHY: Coverage gap blocking CI quality gate / production confidence.
  FILES:
    - tests/test_[module].py (create or extend)
    - [source files under test]
  DONE_CRITERIA:
    - pytest tests/test_[module].py -v passes with 0 failures
    - Coverage for [module] reaches [Y]% (pytest --cov=[module] --cov-report=term)
    - Tests cover: happy path, [error case 1], [error case 2], edge case [X]
    - No mocks that make tests meaningless (mock only external I/O)
  NOTES: [Existing fixtures available in conftest.py, any tricky state to set up]
risk: safe
estimated_tokens: medium
dependencies: []
```

## Research / ADR

```yaml
title: "Research and draft ADR: [topic]"
description: |
  WHAT: Research [topic] and write an Architecture Decision Record.
  WHY: Need documented decision before implementing [feature].
  FILES:
    - docs/adr/[NNN]-[topic].md (create)
  DONE_CRITERIA:
    - ADR exists at docs/adr/ following existing format
    - Covers: Context, Decision Drivers, Options Considered, Decision, Consequences
    - Minimum 3 options evaluated with trade-offs
    - References at least 2 external sources (linked)
  NOTES: [Existing ADRs to reference for format, key constraints to consider]
risk: safe
estimated_tokens: medium
dependencies: []
```

## Boilerplate / Scaffold

```yaml
title: "Scaffold [service/module] with [pattern]"
description: |
  WHAT: Create [service/module] following [pattern]. Generate skeleton, not full impl.
  WHY: Unblocks [team/feature] from starting implementation.
  FILES:
    - [new directory structure]
  DONE_CRITERIA:
    - Directory structure matches [reference/pattern]
    - All files importable without errors (python -c "import [module]")
    - README.md present with [sections]
    - Placeholder tests exist and pass
  NOTES: [Pattern to follow, existing examples at [path]]
risk: safe
estimated_tokens: low
dependencies: []
```

## Argo Workflow Template (REVIEW — unlock required)

```yaml
title: "Add Argo Workflow template for [operation]"
description: |
  WHAT: Create WorkflowTemplate for [operation] in [repo]/workflows/[category]/.
  WHY: [Operation] currently manual. Needed for [milestone].
  FILES:
    - workflows/[category]/[name].yaml
    - workflows/[category]/base/ (reference primitives)
  DONE_CRITERIA:
    - argo lint workflows/[category]/[name].yaml passes
    - WorkflowTemplate spec validates against schema
    - Template follows base/ + apps/ primitive/operator/orchestrator taxonomy
    - serviceAccountName, namespace, and resource limits set correctly
  NOTES: [Existing templates to reference, required parameters, secret refs]
risk: review
estimated_tokens: medium
dependencies: []
```

## Terraform Module (RISKY — explicit unlock required)

```yaml
title: "Add Terraform module for [resource]"
description: |
  WHAT: Create/modify Terraform for [resource] in [environment].
  WHY: [Infrastructure need]
  FILES:
    - terraform/[path]/[module]/ 
  DONE_CRITERIA:
    - terraform validate passes
    - terraform plan shows ONLY expected changes (no unexpected destroys)
    - Plan output saved to .claude/scratchpads/[task-id]-tfplan.txt
    - Variables documented in variables.tf with descriptions
    - NO terraform apply (human reviews plan and applies)
  NOTES: [State backend, workspace, required provider versions, blast radius]
risk: risky
estimated_tokens: high
dependencies: []
```

---

## Planning Session Prompt Template

Use this to kick off a PLAN session with Claude:

```plaintext
Morning shift planning for [date].

Repos in scope: [list]
Available time budget: ~[N] hours of agent work

Work I want done:
1. [item]
2. [item]
3. [item]

Constraints:
- Do NOT touch [X] (in flux / someone else working on it)
- [Any prod freeze / deployment windows]
- Risk tolerance: conservative (default risky=blocked) / moderate / open

Decompose this into a task list. Interview me if anything is ambiguous before
creating the Tasks API entries.
```
