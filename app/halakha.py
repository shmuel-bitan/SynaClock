import json
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "halakhot.json"

_cache = {"mtime": None, "data": None}


def load_bank():
    """Load the local halakha bank and automatically refresh when the JSON changes."""
    if not DATA_FILE.exists():
        return None
    mtime = DATA_FILE.stat().st_mtime_ns
    if _cache["data"] is None or _cache["mtime"] != mtime:
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or not isinstance(data.get("halakhot"), list):
            raise ValueError("data/halakhot.json: format invalide (clé 'halakhot' attendue)")
        _cache.update(mtime=mtime, data=data)
    return _cache["data"]


def _public(item, campaign=None):
    if not item:
        return None
    return {
        "id": item.get("id"),
        "title": item.get("occasion_he") or "הלכה יומית",
        "content": item.get("text_he") or "",
        "source": item.get("reference_he") or "",
        "source_url": item.get("source_url") or "",
        "category": item.get("category") or "daily",
        "campaign": campaign,
    }


def _holiday_start(title: str):
    """Map only the *first* day/candle of a festival to a SynaClock campaign.

    Hebcal is requested in Hebrew. Restricting the match to the first day avoids
    accidentally starting a new 30-day campaign while the festival is already underway.
    """
    t = (title or "").strip()
    if t == "פורים" or t.startswith("פורים "):
        return "purim"
    if t.startswith("פסח א") or t in {"ערב פסח", "פסח"}:
        return "pesach"
    if t.startswith("סוכות א") or t in {"ערב סוכות", "סוכות"}:
        return "sukkot"
    if ("חנוכה" in t and ("א׳" in t or "א'" in t or "1" in t)) or t in {"ערב חנוכה", "חנוכה"}:
        return "hanukkah"
    return None


def select_for_day(day: date, calendar_items=None, prefer_shabbat=True):
    """Select the halakha for *day* from the local bank.

    Priority: 30-day festival campaign > optional Shabbat bank > daily rotation.
    calendar_items should contain Hebcal events from today through at least +30 days.
    """
    bank = load_bank()
    if not bank:
        return None
    items = bank.get("halakhot", [])

    # 30-day pre-festival campaigns.
    for event in sorted(calendar_items or [], key=lambda x: x.get("date", "")):
        try:
            event_day = date.fromisoformat(str(event.get("date", ""))[:10])
        except ValueError:
            continue
        delta = (event_day - day).days
        if not 1 <= delta <= 30:
            continue
        category = _holiday_start(event.get("title", ""))
        if not category:
            continue
        match = next((h for h in items if h.get("category") == category and h.get("days_before_occasion") == delta), None)
        if match:
            return _public(match, {"category": category, "days_before": delta, "date": event_day.isoformat()})

    # Optional Shabbat rotation. Using weeks since an arbitrary Monday makes the
    # selection deterministic across restarts and machines.
    if prefer_shabbat and day.weekday() == 5:
        shabbat = sorted((h for h in items if h.get("category") == "shabbat"), key=lambda h: h.get("rotation_order") or 0)
        if shabbat:
            week_index = day.toordinal() // 7
            return _public(shabbat[week_index % len(shabbat)], {"category": "shabbat"})

    daily = sorted((h for h in items if h.get("category") == "daily"), key=lambda h: h.get("rotation_order") or 0)
    if not daily:
        return None
    return _public(daily[(day.toordinal() - 1) % len(daily)], {"category": "daily"})
