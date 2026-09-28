from datetime import date, timedelta
import httpx
from .firestore_store import cache_get, cache_put

BASE = "https://www.hebcal.com"


def _get(path, params, key):
    try:
        with httpx.Client(timeout=12, headers={"User-Agent": "SynaClock/4.0"}) as client:
            response = client.get(BASE + path, params=params)
            response.raise_for_status()
            data = response.json()
            cache_put(key, data)
            return data, False
    except (httpx.HTTPError, ValueError):
        cached = cache_get(key)
        if cached is None:
            raise
        return cached, True


def zmanim(cfg, day=None):
    d = day or date.today()
    key = f"zmanim:{d.isoformat()}:{cfg['latitude']}:{cfg['longitude']}:{cfg['timezone']}"
    params = {
        "cfg": "json", "date": d.isoformat(), "latitude": cfg["latitude"],
        "longitude": cfg["longitude"], "tzid": cfg["timezone"], "sec": 1,
    }
    return _get("/zmanim", params, key)


def calendar(cfg, start=None, days=35):
    s = start or date.today(); e = s + timedelta(days=days)
    key = f"calendar:{s}:{e}:{cfg['latitude']}:{cfg['longitude']}:{cfg['timezone']}:{cfg['israel']}"
    params = {
        "v": 1, "cfg": "json", "start": s.isoformat(), "end": e.isoformat(), "maj": "on", "min": "on",
        "mod": "on", "nx": "on", "mf": "on", "ss": "on", "s": "on", "c": "on", "geo": "pos",
        "latitude": cfg["latitude"], "longitude": cfg["longitude"], "tzid": cfg["timezone"],
        "i": "on" if cfg.get("israel") else "off", "lg": "he",
        "b": cfg.get("candle_lighting_minutes", 18),
    }
    return _get("/hebcal", params, key)


def hebrew_date(day=None):
    d = day or date.today(); key = f"hdate:{d.isoformat()}"
    return _get("/converter", {"cfg": "json", "g2h": 1, "date": d.isoformat(), "lg": "he"}, key)
