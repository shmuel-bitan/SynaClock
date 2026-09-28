import json
import os
from pathlib import Path
from zoneinfo import ZoneInfo

PATH = Path(__file__).resolve().parent.parent / "config.json"


def _bool(v, default=False):
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on", "oui"}


def load_config():
    data = {}
    if PATH.exists():
        data = json.loads(PATH.read_text(encoding="utf-8"))

    # Vercel/environment values override config.json. Secrets should live only here.
    mapping = {
        "synagogue_name": "SYNAGOGUE_NAME",
        "city": "SYNAGOGUE_CITY",
        "timezone": "SYNAGOGUE_TIMEZONE",
        "admin_password": "SYNACLOCK_ADMIN_PASSWORD",
    }
    for key, env_name in mapping.items():
        if os.getenv(env_name):
            data[key] = os.getenv(env_name)

    if os.getenv("SYNAGOGUE_LATITUDE"):
        data["latitude"] = float(os.getenv("SYNAGOGUE_LATITUDE"))
    if os.getenv("SYNAGOGUE_LONGITUDE"):
        data["longitude"] = float(os.getenv("SYNAGOGUE_LONGITUDE"))
    if os.getenv("SYNAGOGUE_ISRAEL") is not None:
        data["israel"] = _bool(os.getenv("SYNAGOGUE_ISRAEL"))
    if os.getenv("CANDLE_LIGHTING_MINUTES"):
        data["candle_lighting_minutes"] = int(os.getenv("CANDLE_LIGHTING_MINUTES"))

    data.setdefault("synagogue_name", "SynaClock")
    data.setdefault("city", "")
    data.setdefault("timezone", "Europe/Paris")
    data.setdefault("latitude", 48.8566)
    data.setdefault("longitude", 2.3522)
    data.setdefault("israel", False)
    data.setdefault("candle_lighting_minutes", 18)

    ZoneInfo(data["timezone"])
    if not (-90 <= float(data["latitude"]) <= 90):
        raise ValueError("latitude invalide")
    if not (-180 <= float(data["longitude"]) <= 180):
        raise ValueError("longitude invalide")
    return data
