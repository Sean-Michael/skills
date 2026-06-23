# Recreation.gov permit API reference

Reverse-engineered for camp-based wilderness permits. North Cascades NP Backcountry
= permit id **4675322**. All endpoints are public/no-auth but **403 without a
browser-shaped User-Agent**. Base: `https://www.recreation.gov/api`.

## Stable JSON endpoints (used by `permits.py`)

| Endpoint | Returns |
| --- | --- |
| `GET /permitcontent/{id}/permit` | Permit overview (name, etc.) |
| `GET /permitcontent/{id}/divisions` | ~880KB. Every camp/zone keyed by id. Fields: `name`, `district` (== "Starting Area" chip), `latitude`/`longitude`, `type`, `fees` (amount in **cents**), `is_active`, `is_hidden`, `is_lottery_option`, `status`, `child_distances` (inter-camp mileage), `entry_ids`/`exit_ids`. |
| `GET /permitseason/display/{id}/{YYYY-MM-DD}` | Season config: `start_date`, `end_date`, `display_start` (general on-sale date), `display_time`, `timezone`. Date-independent. |
| `GET /permitseason/display/eap/{id}/{date}` | Early-access lottery config. |

Tried and **404**: `/permits/{id}/availability[/month]`, `/permits/{id}/divisions/availability`,
`/permits/{id}/availabilityv2`. There is no clean availability JSON for this permit type.

## Availability grid (scraped by `availability.py`)

Rendered only in the SPA, after selecting a Starting Area **and** a group size.

- Page: `https://www.recreation.gov/permits/{id}/registration/detailed-availability?date=YYYY-MM-DD`
  (direct nav often fails to hydrate — go via the permit page's "Check Availability" button).
- Set party size: "Add Group Members…" button → `button[aria-label='Add Peoples']`
  stepper → "Close". Grid shows "Information Required" until a size is set.
- Use the **"Daily Groups"** tab for per-site counts.
- Cell DOM:
  ```html
  <div data-testid="division-availability-cell" role="gridcell"
       class="rec-grid-grid-cell walk-up">      <!-- 2nd class = status -->
    <button class="rec-availability-date"
            aria-label="Basin Creek Camp on June 23, 2026 - Walk-Up">
      <span>…count…</span>                       <!-- cell text = remaining -->
  ```
  Status classes seen: `available`, `walk-up`, `reserved`, `unavailable`.
  aria-label format: `"<Site> on <Month Day, Year> - <Status>"`.
- Pagination buttons: **"View Next 5 Days"** / **"View Prev 5 Days"** (~10 cols shown).

## NOCA 2026 booking rules (from the permit page)

Lottery applications Mar 2–13 · results Mar 20 · early-access reservations Mar 24–Apr 21
· **general on-sale Apr 29, 7am PT** · season May 15–Oct 10 · reserve ≥2 days ahead ·
pickup by 11am on day 1 or released · 60% reservable online / 40% walk-up · max daily
mileage between camps is enforced in the grid · WIC: (360) 854-7245, Marblemount WA.
