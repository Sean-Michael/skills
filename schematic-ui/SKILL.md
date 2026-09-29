---
name: schematic-ui
description: Design language for UIs in the Japanese software-engineering design ethos — Ma (negative space as active interval), Shibui (understated elegance), and jōhō-mitsu (functional information density). Text-dense, ledger-like, explicitly labeled, retro-industrial, schematic in feel; the PlayStation/Sony precision lineage applied to software. Use this skill whenever the user asks for a UI, web app, dashboard, menu, control panel, admin tool, or prototype and wants it minimalist-functional, schematic-like, technical, device-like, timeless, or "Japanese software" in feel.
---

# Schematic UI

Design in the ethos of great Japanese software and device interfaces: functional minimalism fused with a retro, text-dense engineering sensibility. The result should feel simultaneously mechanical and timeless — a precision instrument, a well-kept ledger, a beautifully drafted schematic. Two ideas govern everything:

**Ma (間)** — negative space as an active, breathing interval, not an empty void. Space is spent deliberately to give weight and utility to interactive elements and to frame dense regions so they read as single deliberate figures.

**Shibui** — understated elegance. Nothing announces itself. Beauty comes from proportion, alignment, and restraint, and the design ages gracefully because it never chased a trend.

Import the engineering discipline, never cultural costume: no decorative foreign-language text, no locale theming, no iconography borrowed from national identity. The multi-script typographic tradition contributes its *discipline* — rigorous alignment, consistent rhythm across mixed character systems — which applies fully to Latin-only interfaces. Only set actual Japanese text when the product is genuinely localized.

This is a design-direction skill: it supplies the aesthetic point of view. General design process guidance (planning passes, self-critique, copywriting) still applies — resolve every open aesthetic decision using this document.

## Principles

1. **Two-second comprehension.** The screen's job must be understandable at a glance. A dense screen can pass this test when its structure is honest; if a screen needs explanation, redesign it.

2. **Explicit over ambiguous.** Favor descriptive text labels and precise instructions over cryptic icons. A labeled action is high-trust; an unlabeled glyph is a guess the user must make. Icons are secondary reinforcement at most, drawn as pure geometry at one stroke weight, and a bare glyph is acceptable only for universally fixed meanings (close ×, back ‹). When in doubt, write the word.

3. **Functional density (jōhō-mitsu).** Unlike whitespace-heavy minimalism, this language embraces structured information density: text and data *are* the visual hierarchy. Ledger-like tables, aligned columns, many values on screen — all correct, provided the grid is rigid: consistent row heights, mathematical spacing (4/8px scale), columns that truly align, hairline separation. Density without grid discipline is chaos; density with it is authority.

4. **Ma frames the density.** Generous margins around dense regions, real breathing room around primary actions, deliberate intervals between functional zones. The contrast between packed figure and open interval is the composition — space gives weight to what it surrounds.

5. **Monochrome first, color as signal.** The base must fully work in grayscale. One accent hue carries identity and selection (deep signal blue, #0070D1 territory, unless the brief supplies a brand color). On near-black surfaces #0070D1 falls below 4.5:1, so lift it a step (≈#3D8FE0) wherever the accent carries text. Semantic color appears only as state: green = healthy/proceed, amber = pressure/pending, red = fault/stop. Never a second identity accent; never color as decoration.

6. **Material honesty.** Components declare their digital affordances plainly: buttons look like buttons (bordered or filled rectangles with visible pressed states), data containers look like ledgers, inputs look like fields. No affordance hidden behind hover, no flat text secretly clickable, no decoration pretending to be function or function disguised as decoration.

7. **Durability over novelty.** Choose what will still look correct in fifteen years: high-contrast tables, rigid structure, restrained radii (0–6px, chosen once), and unapologetic workhorse typography. The system font stack (`system-ui`) is a legitimate, even ideal, choice — early-2000s desktop precision is a feature, not a limitation. Resist every fleeting fad by default.

8. **Feedback is instant and calm.** Every interactive element responds within ~100ms, but precisely, not bouncily: a surface steps one shade, an accent rule appears, an outline draws in. The machine is confident; it never jiggles.

## Visual system

**Surfaces.** Matte and flat: near-black (#0E0F11–#16181B) or paper-neutral (#F4F4F1) bases, panels differentiated by a single surface step or a hairline — never shadows-as-styling, gradients, or glass. Either register works; pick per brief and hold it.

**Lines.** Hairlines (1px, low opacity) are the primary structural device: rules between ledger rows, a heavier 2px rule under table headers, frame ticks at panel corners. Every line must mean a boundary, a scale, or a connection — as in a schematic, no line is decorative. Low opacity is for structure only: borders that identify a control (inputs, buttons, checkboxes) must hold 3:1 against their surface.

**Type.** Two voices. Headings and controls in a workhorse sans — `system-ui` or a plain grotesk (Inter, Space Grotesk) — and all data, values, designations, and annotations in monospace (IBM Plex Mono, JetBrains Mono, or the system mono stack). The signature register is the micro-label: 10–11px uppercase, letterspaced .15–.2em, muted — for zone names, designations ("NODE 04", "SYS / READY"), and units. All numbers tabular (`font-variant-numeric: tabular-nums`); values always carry units. Secondary text may sit at mid-gray — hierarchy through weight and tone is correct — but primary content stays high-contrast and interactive labels never fall below 13px.

**Tables are first-class.** The ledger table is the centerpiece component, not a fallback: explicit column headers, right-aligned numerics, state expressed as a text word (optionally color-toned), row selection marked by a 2px accent rule on the leading edge plus a faint accent wash. Give `:focus-visible` the identical treatment — keyboard navigation should look native, like a cursor moving through a console menu.

**Controls.** Precise rectangles: hairline border or single-step fill, generous padding, explicit text label. The primary action is distinguished by the accent, not by size inflation. Touch targets still meet 44px height — precision lives in the drawing, not in miniaturization. A back/cancel path is always visible, always in the same place.

## Motion

Calm and exact: 150–250ms, standard ease, opacity plus a 2–4px translate; rules and outlines may draw in. One slow ambient element is allowed as the signature — a breathing status indicator, a ticking readout — the way a console home screen is alive without moving. No bounce, no parallax, no scroll theatrics. Respect `prefers-reduced-motion` by removing ambient motion and transitions while keeping instant state changes.

## Voice

Labels are designations, not sentences: "NODE 04", "MEM / 78%", "OUTPUT A". Actions are explicit verbs, written out: "Drain node", "Confirm order", "Save changes" — never bare symbols. State messages are declarative: "READY", "SYNCING", "FAULT — reseat drive". Instructions are precise and complete rather than clever. No exclamation points, no apology, no filler; warmth arrives through care and precision, not chattiness.

## What to refuse

These break the language; treat them as bugs:
- Icon-only actions; cryptic glyphs where a word would do
- Decoration of any kind: gradients, glassmorphism, shadows as styling, illustrative icons, emoji
- A second accent color, or semantic colors used decoratively
- Whitespace inflation that dilutes the data — but equally, density without grid discipline
- Trend-chasing: pill-everything, oversized rounded cards, bouncy or springy motion, skeleton shimmer (use a plain "SYNCING" state)
- Hairlines or annotations that don't mean anything
- Hover as the only affordance signal; flat text that is secretly a button
- Cultural signifiers as decoration: untranslated foreign text, national or locale theming the brief didn't ask for
- Illegible contrast — muted is a tone, not an excuse

## Self-check before delivering

View it in grayscale: does the hierarchy fully survive? Squint: is the primary action still obvious, and does the dense region read as one deliberate figure? Ask of every line, label, and interval: what does this one mean? Tab through: does focus look designed? Would this interface still look correct in fifteen years, and would it work unchanged in any country? If any answer is no, fix it before showing the result.
