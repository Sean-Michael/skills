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
   every reachable state. Include empty/zero-data states.

2. **Infer the UI personality** from what exists — observe border-radius, font
   choices, color palette, and copy tone. Classify as elegant (serif, sharp
   corners, restrained palette), playful (rounded, saturated, casual copy), or
   neutral (sans-serif, medium radius, professional). Flag inconsistencies —
   e.g. playful rounded buttons with formal serif headings.

3. **Fix issues immediately** by injecting CSS and JS via Playwright. Take
   before/after screenshots to confirm improvements.

4. **Re-audit after each round** of fixes — new issues surface once earlier
   ones are resolved. Keep iterating until the design is coherent and polished.

5. **Update the codebase** to make changes permanent. Do not introduce bloat
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

---

## Relationships & Composition

### Button Hierarchy

When multiple actions compete, only **one** gets primary treatment:

| Role        | Style                                         |
|-------------|-----------------------------------------------|
| Primary     | Solid fill, brand color, prominent             |
| Secondary   | Outline or muted fill                          |
| Tertiary    | Ghost / text-only link style                   |
| Destructive | Tertiary or secondary — never red primary alongside other primaries |

- If "Delete", "Edit", and "Publish" all look equally bold, the user can't
  tell what the intended action is. Demote everything except the one thing you
  want the user to do.

### Label Elimination

- **Format is the label** — `john@example.com` doesn't need an "Email:" prefix.
  Dates, phone numbers, currency, and URLs are self-evident.
- **Combine label into value** — instead of "In stock: Yes", say "In stock" as
  styled text or a badge.
- **De-emphasize labels** — when labels are necessary, make them smaller, lighter
  weight, and lower contrast than their values.
- **Exception**: dense specification/comparison tables benefit from labels for
  scannability.

### Spacing as Grouping

- Elements that belong together must be **closer** to each other than to
  unrelated elements — title tight to its body, generous gap before the next
  section.
- Ambiguous equidistant spacing makes relationships unclear. Audit title-to-body
  vs. body-to-next-title distances. Audit icon-to-label gaps vs. label-to-label
  gaps in lists.

### Border Alternatives

- Prefer **box-shadow**, **background color differences**, and **extra spacing**
  over `border: 1px solid`. Borders between every element create visual clutter.
- Borders are fine for inputs and explicit dividers, but a list of cards
  separated only by gap + shadow reads cleaner than bordered rows.

---

## Grids, Layout & Spacing

- All spacing must be multiples of **4px** — audit margins, paddings, gaps.
- Whitespace generous enough that content breathes.
- Consistent alignment — no orphaned elements, no ragged gutters.
- Related elements tight together, unrelated elements separated generously.

---

## Typography & Font Sizing

- Consistent type scale — flag arbitrary font sizes not on the scale.
- Weight and size together signal hierarchy — not one without the other.
- Body `line-height`: 1.4–1.6× font size. Large headings can go tighter (~1.1–1.2).
- Wide content columns need taller line-height (~1.6–1.8); narrow columns can
  use shorter (~1.4–1.5).
- Max 2 typefaces, max 3 weights in active use.
- **Letter spacing**: tighten large headlines (`letter-spacing: -0.02em` to
  `-0.05em`). Loosen all-caps text (`letter-spacing: 0.05em`+).

---

## Content Constraints

- **Line length**: paragraphs should be **45–75 characters** wide. Audit with
  `ch` units or measure rendered text. Applies even when the element shares a
  row with images or sidebars.
- **Don't fill the whole screen**: content areas need a `max-width` — just
  because the nav is full-width doesn't mean the body should be. A checkout
  page or article at 600–800px centered reads far better than stretched to 1400px.
- **Think in columns**: when a single column feels too wide on desktop but works
  on mobile, consider splitting into 2–3 columns rather than just making it wider.
- **Scale disproportionately**: when adapting components across breakpoints,
  fine-tune padding, font-size, and icon-size independently — don't scale all
  properties by the same factor.

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

## Empty States

- Every content-dependent view must have an intentional empty state — not just
  a blank page.
- Show a prominent CTA ("+ Add contact", "Create your first project") as the
  main focus.
- **Hide irrelevant chrome**: tabs, filters, sort controls, and bulk actions
  should be hidden or disabled when there's zero content. Showing them empty
  creates confusion.
- An illustration or icon reinforces the empty state message and prevents the
  page from feeling broken.

---

## User-Uploaded Content

- Control shape and size: center user images in fixed-dimension containers and
  crop overflow. Never let aspect ratios break your layout.
- Prevent background bleed on avatars and thumbnails — when a user uploads an
  image with a white or light background, it bleeds into your page background.

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
- **Borders everywhere** — lists, cards, and sections separated by `border`
  instead of shadow, background, or spacing
- **Content stretching full viewport** — paragraphs or forms at 100% width with
  no `max-width` constraint
- **Paragraph lines > 75 characters** — hard to read; constrain with `max-width`
  in `ch` or `px`
- **Multiple equally-styled primary buttons** — competing CTAs with no clear
  hierarchy
- **Redundant labels** on self-evident data — "Email: user@example.com",
  "Date: March 5, 2025"
- **Empty views with no CTA** — blank pages with no guidance on what to do next
- **User-uploaded images without dimension control** — breaking layout or
  bleeding into page background
- **Personality inconsistency** — mixing sharp corners with bubbly fonts, or
  playful colors with formal copy

---

## CSS Techniques — Non-Obvious Patterns

### Prevent avatar/thumbnail background bleed

```css
.avatar {
  box-shadow: inset 0 0 0 1px rgba(0, 0, 0, 0.1);
  /* OR */
  border: 1px solid rgba(0, 0, 0, 0.05);
}
```

### Overlap elements for depth (hero → content)

```css
.search-panel {
  position: relative;
  margin-top: -60px; /* pulls up into the hero section */
}
```

### Two-shadow combination for realistic depth

```css
.card {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.12),   /* tight, dark — defines edge */
    0 8px 24px rgba(0, 0, 0, 0.08);   /* wide, soft — ambient lift */
}
```

### Accent border for instant personality

```css
.card  { border-top: 4px solid var(--color-primary); }
.alert { border-left: 4px solid var(--color-warning); }
```
