"""Cancellation watch for Recreation.gov permits.

Re-scrapes availability and reports sites that became reservable since the last
run (cancellations open up constantly). Stateless across processes via a small
JSON state file, so it works fine driven by cron / a scheduler.

  python watch.py --area "Cascade Pass Area" --start 2026-07-04 --nights 3 \
      --group 2 --sites "Sahale Glacier Camp,Pelton Basin Camp"

  # poll loop (or schedule the single-shot form externally):
  python watch.py --area "..." --start ... --nights ... --loop 1800

Prints newly-open `{site, date, remaining}` lines to stdout and exits non-zero with
nothing new (so a scheduler can alert only on output). Restrict to the sites you
care about with --sites; omit to watch every site in the area.

Read-only — it watches, it does not book. Keep the interval polite (>= ~15 min).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import date

import availability as av


def _open_keys(rows: list[dict], sites: set[str] | None) -> dict[str, int]:
    """Map of 'site|date' -> remaining, for cells reservable online right now."""
    out = {}
    for r in rows:
        if r["status"] == "available" and (r["remaining"] or 0) > 0:
            if sites and r["site"] not in sites:
                continue
            out[f"{r['site']}|{r['date']}"] = r["remaining"]
    return out


def _load(path: str) -> dict:
    if path and os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def check(permit: str, area: str, start: date, nights: int, group: int,
          sites: set[str] | None, state_path: str, headed: bool) -> list[dict]:
    rows = av.scrape(permit, start, nights, [area], all_areas=False,
                     group=group, headed=headed, debug=False)
    now = _open_keys(rows, sites)
    prev = _load(state_path)
    new = [{"site": k.split("|")[0], "date": k.split("|")[1], "remaining": v}
           for k, v in now.items() if k not in prev]
    if state_path:
        with open(state_path, "w") as f:
            json.dump(now, f)
    return new


def main():
    ap = argparse.ArgumentParser(description="Watch rec.gov permit cancellations")
    ap.add_argument("--permit", default=av.__dict__.get("NOCA_PERMIT_ID", "4675322"))
    ap.add_argument("--area", required=True)
    ap.add_argument("--start", required=True)
    ap.add_argument("--nights", type=int, default=2)
    ap.add_argument("--group", type=int, default=2)
    ap.add_argument("--sites", help="comma-separated site names to watch (default: all)")
    ap.add_argument("--state", default="watch_state.json", help="state file path")
    ap.add_argument("--loop", type=int, help="poll every N seconds instead of one-shot")
    ap.add_argument("--headed", action="store_true")
    a = ap.parse_args()

    start = date.fromisoformat(a.start)
    sites = {s.strip() for s in a.sites.split(",")} if a.sites else None

    def once() -> int:
        new = check(a.permit, a.area, start, a.nights, a.group, sites, a.state, a.headed)
        if new:
            for n in new:
                print(f"OPEN: {n['site']}  {n['date']}  ({n['remaining']} left)  "
                      f"-> https://www.recreation.gov/permits/{a.permit}"
                      f"/registration/detailed-availability?date={a.start}")
            return 0
        print("(no new openings)", file=sys.stderr)
        return 1

    if a.loop:
        while True:
            once()
            time.sleep(max(60, a.loop))
    else:
        sys.exit(once())


if __name__ == "__main__":
    main()
