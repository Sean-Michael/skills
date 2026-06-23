---
name: permit-recon
description: >-
  Find and report Recreation.gov backcountry permit details for a trip — when to
  apply (lottery/on-sale timing + live availability), where (which camps a route
  maps to + which Starting Area), and exactly what to enter to book. Use when the
  user asks about backcountry/wilderness permits, campsite or permit availability,
  "what permits do I need", a North Cascades (or other rec.gov camp-based) trip, or
  wants a cancellation watch. Recon only — it never books.
---

# Permit Recon

Turn a trip idea ("permits for a 4th-of-July backcountry trip") into a concrete
**when / where / what** briefing, backed by live Recreation.gov data. Built for
North Cascades NP (permit `4675322`) but works for any camp-based rec.gov permit —
only the permit id changes.

**Hard rule: recon only.** Never log in, select, or submit a booking — that
violates rec.gov's ToS and is bot-protected. Produce the inputs + a deep link and
let the user click submit. Do not enter credentials or payment.

## Scripts (reusable, in `scripts/`)

Run from `scripts/`. First-time setup for the Playwright piece:
`python -m venv .venv && .venv/bin/pip install playwright && .venv/bin/python -m playwright install chromium`
(a `.venv` may already be present). The pure-data scripts need no deps beyond stdlib.

| Script | What it does | Network |
| --- | --- | --- |
| `permits.py` | Camps (name/district/lat-lon/fees), season + on-sale/lottery timing, and route→camp matching (haversine). Pure JSON APIs. | fast, no browser |
| `availability.py` | Live per-camp×date grid via headless Playwright (the grid isn't a clean API). Emits `{area,site,date,status,remaining}`; status ∈ available/walk_up/reserved/unavailable. | browser |
| `recon.py` | Fuses the two: ROUTE mode (planned camps → match → live status per night) and BROWSE mode (area + dates → what's open). The main entrypoint. | browser |

## Workflow

1. **Pin the permit.** Default North Cascades `4675322`. For a different
   park/area, find its permit id first (WebSearch "<area> backcountry permit
   recreation.gov" → the `/permits/<id>` URL) and pass `--permit <id>`.

2. **Get the trip shape.**
   - If the user has a Routeguide trip / GPX, use its camp markers (lat/lon in
     order) as ROUTE mode input — write them to a JSON file
     `[{"name","lat","lon"}, ...]` and run `recon.py --planned`.
   - If they just named dates/area ("3 nights around Cascade Pass over July 4"),
     use BROWSE mode (`recon.py --area "<Starting Area>" --start ... --nights ...`).
   - Party size matters (availability is per group size) — ask if unstated;
     default `--group 2`.

3. **Run recon.**
   ```
   # route mode
   python recon.py --start 2026-07-04 --group 2 --planned trip.json
   # browse mode
   python recon.py --start 2026-07-04 --nights 3 --area "Cascade Pass Area"
   ```
   Starting Area names are the `district` values (also the chips on the booking
   page): Beavers-Whatcom Pass, Boulder Creek-Purple Pass, Cascade Pass Area,
   Copper-Chilliwack, Diablo-Ross Lake Boat-In, East Bank Trail, Rainbow-McAlester,
   Thunder-Fisher-Park Creek-Panther, Twisp-Bridge Creek-North Fork, Stehekin/Other,
   Short Trails, Cross Country Zones (North/South), High Use Cross Country Zones.

4. **Report when / where / what**, then the live per-night status and a bottom
   line. Read the status honestly:
   - `available` + `remaining>0` → reservable online now; give the booking link.
   - `available` + `remaining 0` → reservable site but full → cancellation-watch
     candidate.
   - `walk_up` → in-station/first-come only (no online reservation); 40% of NOCA
     sites are held for walk-ups at the Wilderness Information Center.
   - `unavailable`/`reserved` → suggest a date shift or a nearby camp/zone in the
     same area, or a cross-country zone.

5. **Timing guardrails to surface every time:** general on-sale date/time, the
   early-access lottery window (NOCA 2026: lottery Mar 2–13, on-sale Apr 29 7am PT,
   season May 15–Oct 10), reserve ≥2 days ahead, and pickup by 11am day-1 or it's
   released.

## Cancellation watch

To catch openings (cancellations are common), poll and diff:
`python watch.py --area "Cascade Pass Area" --start 2026-07-04 --nights 3 --sites "Sahale Glacier Camp" --group 2`
It re-scrapes and prints only newly-open sites. For unattended runs, drive it on a
schedule (e.g. the `/schedule` or `loop` tooling) and alert on a non-empty diff.
Keep the interval reasonable (e.g. every 15–30 min) — don't hammer rec.gov.

## Notes & gotchas

- Availability **requires a group size**; the scraper sets it via the "Add Group
  Members…" popover before the grid renders. Always pass the real party size.
- Use the **"Daily Groups"** view to see per-site counts (the park's own advice).
- rec.gov 403s old User-Agents — the scripts send a current Chrome UA.
- Direct-navigating the availability URL often fails to hydrate; the scraper uses
  the in-app "Check Availability" click path. If selectors break, rec.gov changed
  its markup — re-inspect `div.rec-grid-grid-cell` / `button.rec-availability-date`.
- Endpoint reference: `references/endpoints.md`.
