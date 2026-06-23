"""Live availability scraper for Recreation.gov camp-based wilderness permits.

The per-camp x per-date availability grid is the one thing that is NOT a clean JSON
endpoint (see permits.py for the ones that are): the Recreation.gov SPA renders it
only after you pick a "Starting Area" AND set a group size. This drives a headless
browser through that flow and reads the grid out as structured JSON.

Usage:
    python availability.py --start 2026-07-04 --nights 3 --areas "Cascade Pass Area"
    python availability.py --start 2026-07-04 --nights 3 --all-areas --group 2
    python availability.py --start 2026-07-04 --nights 3 --areas "..." --json out.json
    python availability.py ... --headed --debug

Output (JSON to stdout, or --json file): a list of
    {"area", "site", "date": "YYYY-MM-DD", "status", "remaining"}
where status is one of: available | walk_up | reserved | unavailable.
Only "available" with remaining > 0 is reservable online right now.

Requires:  pip install playwright && playwright install chromium

Read-only recon. It never logs in, selects a booking, or submits anything.

--- How the grid works (reverse-engineered) ---
* Permit page -> "Check Availability" -> detailed-availability grid.
* You must pick a Starting Area (district) and set a group size (the "Add Group
  Members..." popover, "Add Peoples" stepper) before any cells render.
* Each cell: div.rec-grid-grid-cell with a status class (available / walk-up /
  reserved / unavailable); inner button.rec-availability-date has
  aria-label "<Site> on <Month Day, Year> - <Status>"; the cell text is the count.
* "View Next 5 Days" / "View Prev 5 Days" page the date window (~10 cols shown).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

PERMIT_PAGE = "https://www.recreation.gov/permits/{pid}"
# A current Chrome UA — older UAs trigger rec.gov's "unsupported browser" banner.
_UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
       "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36")

_STATUS_FROM_CLASS = {
    "available": "available",
    "walk-up": "walk_up",
    "reserved": "reserved",
    "unavailable": "unavailable",
}


def _log(debug: bool, *a):
    if debug:
        print("[debug]", *a, file=sys.stderr)


def _open_grid(page: Page, permit_id: str):
    """Load a hydrated detailed-availability grid via the click-through path."""
    page.goto(PERMIT_PAGE.format(pid=permit_id), wait_until="domcontentloaded")
    page.get_by_role("button", name="Check Availability").first.click(timeout=20000)
    page.wait_for_selector("text=Select a Starting Area", timeout=25000)


def _set_group_size(page: Page, n: int):
    """Open the group-member popover and bump the party size to `n`."""
    page.get_by_role("button", name="Add Group Members...").first.click(timeout=10000)
    page.wait_for_timeout(700)
    add = page.locator("button[aria-label='Add Peoples']").first
    for _ in range(max(1, n)):
        add.click(timeout=3000)
        page.wait_for_timeout(350)
    page.get_by_role("button", name="Close").first.click(timeout=5000)
    page.wait_for_timeout(2500)


def _select_area(page: Page, area: str) -> bool:
    try:
        page.get_by_role("button", name=area, exact=True).first.click(timeout=8000)
    except PWTimeout:
        try:
            page.get_by_text(area, exact=True).first.click(timeout=5000)
        except PWTimeout:
            return False
    page.wait_for_timeout(2200)
    return True


def _list_areas(page: Page) -> list[str]:
    """Starting Area chip labels, excluding the 'Site or Zone' column header."""
    names = page.evaluate(
        r"""() => [...document.querySelectorAll('button')]
              .map(b => (b.textContent||'').trim())
              .filter(t => t && t.length < 45 &&
                /Pass|Zone|Area|Trail|Lake|Boat|Creek|Stehekin|Short|McAlester|Chilliwack|Panther|Fork/.test(t))"""
    )
    seen, out = set(), []
    for n in names:
        if n not in seen and n != "Site or Zone":
            seen.add(n)
            out.append(n)
    return out


def _read_cells(page: Page) -> list[dict]:
    """Read the currently rendered availability cells into normalized rows."""
    raw = page.evaluate(
        r"""() => [...document.querySelectorAll('div.rec-grid-grid-cell')].map(c => {
              const btn = c.querySelector('button.rec-availability-date');
              return {
                cls: c.className,
                aria: btn ? (btn.getAttribute('aria-label') || '') : '',
                txt:  btn ? (btn.textContent || '').trim() : '',
              };
            })"""
    )
    out = []
    for c in raw:
        aria = c["aria"]
        if not aria:
            continue
        m = re.match(r"^(.*?) on ([A-Z][a-z]+ \d{1,2}, \d{4}) - (.+)$", aria)
        if not m:
            continue
        site, datestr, _status_label = m.groups()
        try:
            iso = datetime.strptime(datestr, "%B %d, %Y").date().isoformat()
        except ValueError:
            continue
        status = "unavailable"
        for token, mapped in _STATUS_FROM_CLASS.items():
            if token in c["cls"]:
                status = mapped
                break
        remaining = int(c["txt"]) if c["txt"].isdigit() else None
        out.append({"site": site.strip(), "date": iso,
                    "status": status, "remaining": remaining})
    return out


def _visible_dates(rows: list[dict]) -> set[str]:
    return {r["date"] for r in rows}


def _paginate_to(page: Page, target: date, debug: bool, max_clicks: int = 30):
    """Click 'View Next 5 Days' until `target` is in the visible window."""
    want = target.isoformat()
    for i in range(max_clicks):
        if want in _visible_dates(_read_cells(page)):
            return True
        try:
            page.get_by_role("button", name="View Next 5 Days").first.click(timeout=5000)
            page.wait_for_timeout(1500)
        except PWTimeout:
            _log(debug, "no Next button at click", i)
            return False
    return False


def scrape(permit_id: str, start: date, nights: int, areas: list[str] | None,
           all_areas: bool, group: int, headed: bool, debug: bool) -> list[dict]:
    want_dates = {(start + timedelta(days=i)).isoformat() for i in range(nights + 1)}
    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(user_agent=_UA,
                                  viewport={"width": 1500, "height": 1100})
        page = ctx.new_page()
        _open_grid(page, permit_id)
        _set_group_size(page, group)

        targets = _list_areas(page) if all_areas else (areas or [])
        _log(debug, "areas to scan:", targets)

        for area in targets:
            if not _select_area(page, area):
                print(f"[warn] could not select area: {area}", file=sys.stderr)
                continue
            _paginate_to(page, start, debug)
            # harvest forward until the whole trip window is covered
            collected: dict[tuple, dict] = {}
            for _ in range(max(1, (nights // 5) + 2)):
                for cell in _read_cells(page):
                    collected[(cell["site"], cell["date"])] = cell
                if want_dates <= {d for (_s, d) in collected}:
                    break
                try:
                    page.get_by_role("button", name="View Next 5 Days").first.click(timeout=5000)
                    page.wait_for_timeout(1400)
                except PWTimeout:
                    break
            for cell in collected.values():
                if cell["date"] in want_dates:
                    results.append({"area": area, **cell})
            _log(debug, f"{area}: {sum(1 for r in results if r['area']==area)} cells in window")
        browser.close()
    results.sort(key=lambda r: (r["area"], r["date"], r["site"]))
    return results


def main():
    ap = argparse.ArgumentParser(description="Scrape live rec.gov permit availability")
    ap.add_argument("--permit", default="4675322")
    ap.add_argument("--start", required=True, help="trip start date YYYY-MM-DD")
    ap.add_argument("--nights", type=int, default=1)
    ap.add_argument("--areas", help="comma-separated Starting Area names")
    ap.add_argument("--all-areas", action="store_true")
    ap.add_argument("--group", type=int, default=2, help="party size to query")
    ap.add_argument("--json", help="write results to this file instead of stdout")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()

    start = date.fromisoformat(a.start)
    areas = [s.strip() for s in a.areas.split(",")] if a.areas else None
    rows = scrape(a.permit, start, a.nights, areas, a.all_areas, a.group, a.headed, a.debug)
    payload = json.dumps(rows, indent=2)
    if a.json:
        with open(a.json, "w") as f:
            f.write(payload)
        print(f"wrote {len(rows)} rows -> {a.json}", file=sys.stderr)
    else:
        print(payload)


if __name__ == "__main__":
    main()
