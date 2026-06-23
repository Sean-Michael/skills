"""Permit recon: fuse route->camp matching (permits.py) with live availability
(availability.py) into one when / where / what / is-it-open answer.

Two modes:

  ROUTE  — you have a planned camp sequence (the camps Routeguide derives from a
           GPX). Snaps them to real permit camps, then checks each night's live
           status on rec.gov:
               python recon.py --start 2026-07-04 --group 2 --planned trip.json
           trip.json: [{"name": "...", "lat": 48.47, "lon": -121.07}, ...]

  BROWSE — you just want to see what's open in an area for some dates:
               python recon.py --start 2026-07-04 --nights 3 --area "Cascade Pass Area"

Recon only — hands you the booking deep link and the exact inputs; never books.
Run from this directory (imports the sibling permits.py / availability.py).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta

import availability as av
import permits as pm


def _status_label(status: str | None, remaining: int | None) -> str:
    if status == "available" and remaining:
        return f"OPEN — {remaining} reservable online"
    if status == "available":
        return "reservable site, but 0 left online (watch for cancellations)"
    if status == "walk_up":
        return "walk-up / in-station only (no online reservation)"
    if status == "reserved":
        return "reserved (taken)"
    if status == "unavailable":
        return "unavailable"
    return "no data (camp not found in grid for this date)"


def route_recon(planned: list[dict], start: date, group: int,
                permit_id: str, headed: bool, debug: bool) -> str:
    recon = pm.build_recon(planned, permit_id)
    nights = len(recon.matches)

    # Live availability for every Starting Area the route touches, across the window.
    live = av.scrape(permit_id, start, nights, recon.starting_areas,
                     all_areas=False, group=group, headed=headed, debug=debug)
    by_site_date = {(r["site"], r["date"]): r for r in live}

    out = [pm.format_recon(recon, start, group), "", "LIVE STATUS (this party size, these dates)"]
    bookable = walkup = blocked = 0
    for m in recon.matches:
        night_date = (start + timedelta(days=m.night - 1)).isoformat()
        cell = by_site_date.get((m.camp.name, night_date))
        status = cell["status"] if cell else None
        remaining = cell["remaining"] if cell else None
        label = _status_label(status, remaining)
        out.append(f"  Night {m.night} ({night_date})  {m.camp.name}: {label}")
        if status == "available" and remaining:
            bookable += 1
        elif status == "walk_up":
            walkup += 1
        else:
            blocked += 1

    out += ["", "BOTTOM LINE"]
    if bookable == nights:
        out.append("  All nights reservable online now — book the itinerary above.")
    elif blocked:
        out.append(
            f"  {blocked}/{nights} night(s) not bookable online. Options: shift the "
            "start date, swap to a nearby camp/zone in the same area, or set a "
            "cancellation watch (see the skill). Walk-up is first-come at the WIC."
        )
    elif walkup:
        out.append(
            f"  {walkup}/{nights} night(s) are walk-up only — secure them in person "
            "at the Wilderness Information Center (40% of sites are held for walk-ups)."
        )
    return "\n".join(out)


def browse_recon(area: str, start: date, nights: int, group: int,
                 permit_id: str, headed: bool, debug: bool) -> str:
    timing = pm.fetch_timing(permit_id)
    live = av.scrape(permit_id, start, nights, [area], all_areas=False,
                     group=group, headed=headed, debug=debug)
    out = [
        f"AVAILABILITY — {area}  (party of {group})",
        f"  On-sale {timing.on_sale_date} {timing.on_sale_time} {timing.timezone}; "
        f"season {timing.season_start} -> {timing.season_end}",
        "",
    ]
    sites: dict[str, list[str]] = {}
    for r in live:
        mark = {"available": f"OPEN({r['remaining']})", "walk_up": "walk-up",
                "reserved": "taken", "unavailable": "x"}.get(r["status"], "?")
        sites.setdefault(r["site"], []).append(f"{r['date'][5:]}={mark}")
    for site, days in sorted(sites.items()):
        out.append(f"  {site}: " + "  ".join(days))
    if not sites:
        out.append("  (no cells returned — check the area name or dates)")
    out += ["", f"  Book/monitor: {av.PERMIT_PAGE.format(pid=permit_id)}"
            f"/registration/detailed-availability?date={start.isoformat()}"]
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Permit recon: match + live availability")
    ap.add_argument("--permit", default=pm.NOCA_PERMIT_ID)
    ap.add_argument("--start", required=True, help="trip start date YYYY-MM-DD")
    ap.add_argument("--group", type=int, default=2)
    ap.add_argument("--planned", help="JSON file: [{name,lat,lon}, ...] (ROUTE mode)")
    ap.add_argument("--area", help="Starting Area name (BROWSE mode)")
    ap.add_argument("--nights", type=int, default=2, help="BROWSE mode trip length")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--debug", action="store_true")
    a = ap.parse_args()
    start = date.fromisoformat(a.start)

    if a.planned:
        with open(a.planned) as f:
            planned = json.load(f)
        print(route_recon(planned, start, a.group, a.permit, a.headed, a.debug))
    elif a.area:
        print(browse_recon(a.area, start, a.nights, a.group, a.permit, a.headed, a.debug))
    else:
        ap.error("provide --planned (route mode) or --area (browse mode)")


if __name__ == "__main__":
    main()
