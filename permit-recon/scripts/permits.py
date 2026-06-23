"""Backcountry permit recon for Recreation.gov camp-based wilderness permits.

Given a planned route (the camp coordinates Routeguide already derives from a GPX
day split), this answers the three questions you actually need before applying:

    WHEN  — the booking timeline: early-access lottery window, general on-sale
            date/time, season bounds, and the "reserve >= N days ahead" rule.
    WHERE — which real permit camps your planned camps map to, and which
            "Starting Area" (district) each lives in — the first thing the
            Recreation.gov booking grid makes you pick.
    WHAT  — the camp-by-night itinerary to enter, group size, and fees.

It does NOT book anything. Automated booking violates Recreation.gov's ToS and is
bot-protected; this is recon only. It hands you a deep link and the exact inputs.

Endpoints (all public, no auth) reverse-engineered from the Recreation.gov SPA:

    GET /api/permitcontent/{id}/divisions          -> every camp/zone: name,
            district, lat/lon, type, fees, group limits, inter-camp distances
    GET /api/permitseason/display/{id}/{date}       -> season window + on-sale
    GET /api/permitseason/display/eap/{id}/{date}   -> early-access lottery config

The live per-camp x per-date availability *grid* is not a clean JSON endpoint: the
SPA renders it only after you pick a Starting Area. `availability_page_url()`
returns the page a browser (Playwright) can drive + scrape for live counts; the
recon below is built from the metadata + timing endpoints, which are stable JSON.

North Cascades NP Backcountry is permit id 4675322. The same shapes apply to other
camp-based Recreation.gov permits (Olympic, parts of the Enchantments, etc.) — only
the id changes.
"""
from __future__ import annotations

import json
import math
import urllib.request
from dataclasses import dataclass, field
from datetime import date

NOCA_PERMIT_ID = "4675322"
_BASE = "https://www.recreation.gov/api"
# Recreation.gov 403s requests without a browser-shaped User-Agent.
_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)

# Districts that are not real backcountry destinations — skip when matching routes.
_NON_TRIP_DISTRICTS = {"NPS Administrative Sites"}


def _get(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": _UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (trusted host)
        return json.load(resp)


def _haversine_mi(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in miles (mirrors gpx._haversine_m, miles instead of m)."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 3958.7613 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@dataclass(frozen=True)
class Camp:
    """A reservable camp or zone (a Recreation.gov permit 'division')."""

    id: str
    name: str
    district: str  # == the "Starting Area" you pick first in the booking grid
    lat: float
    lon: float
    type: str
    reservable: bool
    lottery_option: bool
    reservation_fee_usd: float  # the per-reservation booking fee (separate from nightly use fee)


@dataclass
class Timing:
    """When you can apply, from the permit's season config."""

    season_name: str
    season_start: str  # earliest trip start date reservable
    season_end: str  # latest trip start date reservable
    on_sale_date: str  # general on-sale opens
    on_sale_time: str  # local time it opens
    timezone: str


@dataclass
class CampMatch:
    """A planned camp snapped to the nearest real permit camp."""

    night: int  # 1-based night index in the trip
    planned_name: str
    planned_lat: float
    planned_lon: float
    camp: Camp
    miles_off: float  # distance from planned point to the matched camp


@dataclass
class Recon:
    """The when / where / what answer for a planned trip."""

    permit_name: str
    permit_id: str
    timing: Timing
    matches: list[CampMatch]
    starting_areas: list[str]  # distinct districts the trip touches, in route order
    warnings: list[str] = field(default_factory=list)

    def booking_url(self, start: date) -> str:
        return availability_page_url(self.permit_id, start)


# --- data layer (stable JSON endpoints) -------------------------------------


def fetch_camps(permit_id: str = NOCA_PERMIT_ID) -> list[Camp]:
    """All active, locatable camps/zones for a permit, normalized."""
    payload = _get(f"{_BASE}/permitcontent/{permit_id}/divisions")["payload"]
    camps: list[Camp] = []
    for d in payload.values():
        if not d.get("is_active") or d.get("is_hidden"):
            continue
        lat, lon = d.get("latitude"), d.get("longitude")
        if not lat or not lon:  # zones without a point can't be route-matched
            continue
        res_fee = 0.0
        for f in d.get("fees") or []:
            if f.get("description") == "Reservation Fee":
                res_fee = (f.get("amount") or 0) / 100.0
        camps.append(
            Camp(
                id=d["id"],
                name=d.get("name", "").strip(),
                district=d.get("district", "").strip(),
                lat=float(lat),
                lon=float(lon),
                type=d.get("type", ""),
                reservable=d.get("status", "Open") != "Closed",
                lottery_option=bool(d.get("is_lottery_option")),
                reservation_fee_usd=res_fee,
            )
        )
    return camps


def fetch_timing(permit_id: str = NOCA_PERMIT_ID, on: date | None = None) -> Timing:
    """Season window + general on-sale timing from the permit season config."""
    day = (on or date.today()).isoformat()
    season = _get(f"{_BASE}/permitseason/display/{permit_id}/{day}")["payload"][0]
    return Timing(
        season_name=season.get("name", ""),
        season_start=season.get("start_date", ""),
        season_end=season.get("end_date", ""),
        on_sale_date=season.get("display_start", ""),
        on_sale_time=season.get("display_time", ""),
        timezone=season.get("timezone", ""),
    )


def availability_page_url(permit_id: str, start: date) -> str:
    """The detailed-availability page — drive this with Playwright to read live counts."""
    return (
        f"https://www.recreation.gov/permits/{permit_id}"
        f"/registration/detailed-availability?date={start.isoformat()}"
    )


# --- matching layer ----------------------------------------------------------


def nearest_camp(camps: list[Camp], lat: float, lon: float) -> tuple[Camp, float]:
    """The closest real permit camp to a point, and the distance in miles."""
    best, best_mi = None, math.inf
    for c in camps:
        if c.district in _NON_TRIP_DISTRICTS:
            continue
        mi = _haversine_mi(lat, lon, c.lat, c.lon)
        if mi < best_mi:
            best, best_mi = c, mi
    return best, best_mi  # type: ignore[return-value]


def match_route(camps: list[Camp], planned: list[dict]) -> list[CampMatch]:
    """Snap each planned camp to the nearest real permit camp.

    `planned` is a list of {"name", "lat", "lon"} in trip order — exactly the camp
    markers Routeguide derives from the GPX day split.
    """
    matches = []
    for i, p in enumerate(planned, start=1):
        camp, mi = nearest_camp(camps, p["lat"], p["lon"])
        matches.append(
            CampMatch(
                night=i,
                planned_name=p.get("name", f"Night {i}"),
                planned_lat=p["lat"],
                planned_lon=p["lon"],
                camp=camp,
                miles_off=mi,
            )
        )
    return matches


def build_recon(planned: list[dict], permit_id: str = NOCA_PERMIT_ID) -> Recon:
    """Full when/where/what recon for a planned camp sequence."""
    camps = fetch_camps(permit_id)
    timing = fetch_timing(permit_id)
    matches = match_route(camps, planned)

    # distinct districts in route order = the Starting Areas to pick in the grid
    areas: list[str] = []
    for m in matches:
        if m.camp.district and m.camp.district not in areas:
            areas.append(m.camp.district)

    warnings: list[str] = []
    for m in matches:
        if m.miles_off > 1.0:
            warnings.append(
                f"Night {m.night} '{m.planned_name}' is {m.miles_off:.1f} mi from the "
                f"nearest permit camp ('{m.camp.name}') — no designated camp there; "
                f"you may need a cross-country zone or a different night split."
            )
    if len(areas) > 1:
        warnings.append(
            f"Trip spans {len(areas)} Starting Areas {areas} — the booking grid is "
            "filtered by one area at a time; you'll switch areas as you add nights."
        )

    permit_name = _get(f"{_BASE}/permitcontent/{permit_id}/permit")["payload"].get(
        "name", f"Permit {permit_id}"
    )
    return Recon(
        permit_name=permit_name,
        permit_id=permit_id,
        timing=timing,
        matches=matches,
        starting_areas=areas,
        warnings=warnings,
    )


def format_recon(r: Recon, start: date, group_size: int = 2) -> str:
    """Human-readable when/where/what briefing."""
    nights = len(r.matches)
    res_fee = max((m.camp.reservation_fee_usd for m in r.matches), default=0.0)
    lines = [
        f"PERMIT  {r.permit_name}  (rec.gov #{r.permit_id})",
        "",
        "WHEN",
        f"  Season:        {r.timing.season_start} -> {r.timing.season_end} "
        f"({r.timing.season_name})",
        f"  General on-sale: {r.timing.on_sale_date} at {r.timing.on_sale_time} "
        f"{r.timing.timezone}",
        "  Reserve at least 2 days before your start date; pick up by 11:00 AM "
        "local on day 1 or it's released.",
        "",
        "WHERE  (Starting Area -> pick this first in the grid)",
    ]
    for area in r.starting_areas:
        lines.append(f"  - {area}")
    lines += [
        "",
        f"WHAT TO PUT IN  (start {start.isoformat()}, {nights} night(s), "
        f"group of {group_size}, view = 'Daily Groups')",
    ]
    for m in r.matches:
        flag = f"   [~{m.miles_off:.1f} mi off plan]" if m.miles_off > 1.0 else ""
        lines.append(
            f"  Night {m.night}: {m.camp.name}  ({m.camp.district}){flag}"
        )
    lines += [
        "",
        f"  Reservation fee: ~${res_fee:.2f} (non-refundable) + nightly per-person use fee.",
        f"  Book/monitor: {r.booking_url(start)}",
    ]
    if r.warnings:
        lines += ["", "HEADS UP"]
        lines += [f"  ! {w}" for w in r.warnings]
    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: a 3-night Cascade Pass / Sahale loop (planned camp coords like the ones
    # Routeguide derives from a GPX). Proves the recon end-to-end against live data.
    sample = [
        {"name": "Cascade Pass camp", "lat": 48.4753, "lon": -121.0746},
        {"name": "Pelton Basin", "lat": 48.4690, "lon": -121.0560},
        {"name": "Sahale Glacier Camp", "lat": 48.4810, "lon": -121.0610},
    ]
    recon = build_recon(sample)
    print(format_recon(recon, start=date(2026, 7, 4), group_size=2))
