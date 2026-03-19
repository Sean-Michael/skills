---
name: ui-ux
description: >
  Use when conducting UI/UX audits, fixing visual or interaction design issues,
  or improving the look and feel of a web application. Triggers include: any
  request to audit a UI, improve styling, fix layout or spacing problems,
  enhance accessibility, add hover/focus states, or polish a frontend design.
  Also use when the user mentions Playwright alongside design, CSS, or visual
  quality.
---

# UI/UX Audit & Implementation

## Methodology — Do This First

Before making any changes:

1. **Explore the site fully** via Playwright — navigate every view, interact
   with every control, inspect computed styles, take screenshots. Click through
   every reachable state.

2. **Fix issues immediately** by injecting CSS and JS via Playwright. Take
   before/after screenshots to confirm improvements.

3. **Re-audit after each round** of fixes — new issues surface once earlier
   ones are resolved. Keep iterating until the design is coherent and polished.

4. **Update the codebase** to make changes permanent. Do not introduce bloat
   to the CSS — reuse or refactor what exists.

---

## Affordances & Signifiers

- Group related controls in containers — cards, panels, bordered regions.
- Toggles must live inside a container, never floating.
- Inactive/disabled elements: `opacity ≤ 0.4`, `cursor: not-allowed`.
- Every non-obvious control needs a tooltip on hover.
- Controls must look like what they do — buttons raised, inputs clearly fillable.

---

## Visual Hierarchy

- No flat spreadsheet layouts — every section needs a clear primary element.
- Size, position, and color must work together to direct the eye.
- Most important action or information: largest, highest contrast, most prominent.
- Supporting content should recede — smaller, lighter, lower contrast.


## Grids, Layout & Spacing

- All spacing must be multiples of **4px** — audit margins, paddings, gaps.
- Whitespace generous enough that content breathes.
- Consistent alignment — no orphaned elements, no ragged gutters.
- Related elements tight together, unrelated elements separated generously.


## Typography & Font Sizing

- Consistent type scale — flag arbitrary font sizes not on the scale.
- Weight and size together signal hierarchy — not one without the other.
- Body `line-height`: 1.4–1.6× font size.
- Max 2 typefaces, max 3 weights in active use.

---

## Color Theory

- One primary brand color with a derived ramp — lighter for backgrounds,
  darker for text and accents.
- Semantic colors used consistently and only for their meaning:

| Color  | Meaning |
|--------|---------|
| Blue   | Info    |
| Green  | Success |
| Red    | Error   |
| Yellow | Warning |

- All text must pass **WCAG AA** contrast — `4.5:1` for body, `3:1` for large text.
- Minimal hue count — neutral base + primary + semantics only.

---

## Shadows & Depth

- Raised interactive elements need `box-shadow` — buttons, cards, dropdowns, modals.
- Low opacity, primary-tinted or neutral dark — never pure black.
- Elevation levels: subtle lift for buttons, moderate for cards, strong for modals.
- Flat elements stay flat — don't shadow everything.

---

## Icons & Buttons

- Icon size matches `line-height` of adjacent text — verify with `getComputedStyle`.
- Icon-to-label gap: `4–6px`.
- Button padding: horizontal ≈ 2× vertical — e.g. `8px 16px` or `12px 24px`.
- Minimum click target: `44×44px`.

---

## Feedback & States

Every interactive element must have all required states:

| Element | States                                              |
|---------|-----------------------------------------------------|
| Buttons | default / hover / active / disabled / loading       |
| Inputs  | default / focus / error (red border + message) / success |

- Every meaningful user action must produce a visible response within **300ms**.
- Inject missing states via `:hover`, `:focus`, `:active`, `:disabled` selectors.

---

## Micro-Interactions

- High-value actions get motion — confirmation chips, animated checkmarks, e.g.
  labels morphing to "Saved ✓", copy button should confirm copy happened, etc.
- Timing: `150–300ms`, `ease-out` curves.
- Test live via `page.evaluate()` with CSS transitions and animations.

---

## Overlays & Image Treatments

- Text over images: linear gradients or progressive blur — never flat rectangles.
- Text contrast against overlay must pass `4.5:1`.
- Inject gradient scrims or `backdrop-filter: blur()` where missing.

---

## Anti-patterns

- Floating controls without a containing group
- Flat layouts with no visual hierarchy
- Spacing not on the 4px grid
- Text failing WCAG AA contrast ratios
- Missing hover/focus/active/disabled states
- Pure black box-shadows
- Arbitrary font sizes outside the type scale
- Click targets smaller than 44×44px
