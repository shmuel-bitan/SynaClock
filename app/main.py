from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import base64
import hashlib
import hmac
import json
import os
import re
import secrets

<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Request
=======
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
>>>>>>> 91b0023 (V3)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

<<<<<<< HEAD
=======
import cloudinary
import cloudinary.uploader

>>>>>>> 91b0023 (V3)
from .config import load_config
from .firestore_store import (
    init_store, create, get, list_all, update, delete,
    setting, set_setting, get_shabbat, put_shabbat,
)
from .hebcal import zmanim, calendar, hebrew_date
from .halakha import select_for_day

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="SynaClock API", version="4.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.on_event("startup")
def startup():
    load_config()
    init_store()


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/admin")
def admin():
    return FileResponse(ROOT / "static" / "admin.html")


def safe_cfg():
    cfg = load_config().copy()
    cfg.pop("admin_password", None)
    return cfg


def now_local():
    return datetime.now(ZoneInfo(load_config()["timezone"]))


def _admin_password():
    return str(load_config().get("admin_password") or "")


def _session_secret():
    explicit = os.getenv("SYNACLOCK_SESSION_SECRET")
    if explicit:
        return explicit.encode("utf-8")
    pwd = _admin_password()
    if pwd:
        # Safe enough for local fallback. Production should define SYNACLOCK_SESSION_SECRET.
        return hashlib.sha256(("synaclock-session:" + pwd).encode()).digest()
    return b""


def _sign_session(expires: int):
    payload = str(expires).encode()
    sig = hmac.new(_session_secret(), payload, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(payload + b"." + sig).decode().rstrip("=")


def _verify_session(token: str | None):
    if not token or not _session_secret():
        return False
    try:
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        payload, sig = raw.split(b".", 1)
        expected = hmac.new(_session_secret(), payload, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            return False
        return int(payload.decode()) >= int(datetime.now(timezone.utc).timestamp())
    except Exception:
        return False


def auth(request: Request):
    if not _verify_session(request.cookies.get("synaclock_session")):
        raise HTTPException(401, "Connexion requise")


def parse_iso_time(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def fmt_ztime(value, tz):
    d = parse_iso_time(value)
    if not d:
        return None
    if d.tzinfo:
        return d.astimezone(ZoneInfo(tz)).strftime("%H:%M")
    return d.strftime("%H:%M")


def add_minutes(hhmm, minutes):
    if not hhmm:
        return None
    h, m = map(int, hhmm.split(":"))
    d = datetime(2000, 1, 1, h, m) + timedelta(minutes=minutes)
    return d.strftime("%H:%M")


def _saved_shabbat_program(day: date):
    friday = day if day.weekday() == 4 else day - timedelta(days=1) if day.weekday() == 5 else None
    if not friday:
        return None
    row = get_shabbat(friday.isoformat())
    if not row:
        return None
    payload = row.get("payload") or {}
    key = "friday" if day.weekday() == 4 else "saturday"
    rows = payload.get(key, [])
    out = []
    for i, event in enumerate(rows):
        name = str(event.get("name") or "").strip()
        note = str(event.get("note") or "").strip()
        tm = str(event.get("time") or "").strip()
        if not (name or note or tm):
            continue
        out.append({
            "id": f"poster-{friday.isoformat()}-{key}-{i}",
            "name": name or note or "Événement",
            "event_type": "poster",
            "note": note,
            "time": tm,
            "active": True,
            "sort_order": i,
            "source": "shabbat_poster",
        })
    return out


def resolve_events(day: date, zdata=None):
    special = _saved_shabbat_program(day)
    if special is not None:
        return sorted(special, key=lambda x: (x.get("time") or "99:99", x.get("sort_order", 0)))

    cfg = load_config()
    zdata = zdata or zmanim(cfg, day)[0]
    times = zdata.get("times", {}) if isinstance(zdata, dict) else {}
    wd = day.weekday()
    rows = [r for r in list_all("schedule_events") if r.get("active", True)]
    rows.sort(key=lambda r: (int(r.get("sort_order", 0)), str(r.get("id", ""))))
    out = []
    for row in rows:
        weekdays = str(row.get("weekdays") or "").split(",")
        if str(wd) not in weekdays:
            continue
        if row.get("time_mode") == "fixed":
            tm = row.get("fixed_time")
        else:
            tm = fmt_ztime(times.get(row.get("base_zman")), cfg["timezone"])
            if tm:
                tm = add_minutes(tm, int(row.get("offset_minutes") or 0))
        if tm:
            out.append({**row, "time": tm})
    return sorted(out, key=lambda x: (x.get("time") or "99:99", int(x.get("sort_order", 0))))


def active_announcements():
    now = now_local()
    out = []
    for item in list_all("announcements"):
        if item.get("display_mode", "card") not in {"card", "fullscreen"}:
            continue
        if not item.get("active", True):
            continue
        start = parse_iso_time(item.get("starts_at"))
        end = parse_iso_time(item.get("ends_at"))
        if not start or not end:
            continue
        # datetime-local values are saved without timezone and represent synagogue local time.
        local_now = now.replace(tzinfo=None)
        start_cmp = start.astimezone(now.tzinfo).replace(tzinfo=None) if start.tzinfo else start
        end_cmp = end.astimezone(now.tzinfo).replace(tzinfo=None) if end.tzinfo else end
        if start_cmp <= local_now <= end_cmp:
            out.append(item)
    out.sort(key=lambda x: (-int(x.get("priority", 0)), -int(x.get("id", 0)) if str(x.get("id", "")).isdigit() else 0))
    return out


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "4.1.0-firestore", "time": datetime.now().astimezone().isoformat()}


@app.get("/api/config")
def config():
    return safe_cfg()


@app.get("/api/zmanim")
def api_zmanim(day: str | None = None):
    try:
        d = date.fromisoformat(day) if day else now_local().date()
        data, stale = zmanim(load_config(), d)
        return {"stale": stale, "data": data}
    except Exception as exc:
        raise HTTPException(503, f"Zmanim indisponibles: {exc}")


@app.get("/api/calendar")
def api_calendar():
    try:
        data, stale = calendar(load_config())
        return {"stale": stale, "data": data}
    except Exception as exc:
        raise HTTPException(503, f"Calendrier indisponible: {exc}")


@app.get("/api/date")
def api_date():
    try:
        data, stale = hebrew_date(now_local().date())
        return {"stale": stale, "data": data}
    except Exception as exc:
        raise HTTPException(503, f"Date hébraïque indisponible: {exc}")


@app.get("/api/prayers")
def prayers():
    try:
        zdata, _ = zmanim(load_config(), now_local().date())
        return resolve_events(now_local().date(), zdata)
    except Exception:
        return resolve_events(now_local().date(), {"times": {}})


@app.get("/api/announcements")
def announcements():
    return active_announcements()


@app.get("/api/halakha")
def halakha():
    day = now_local().date()
    try:
        cal, _ = calendar(load_config(), day, 35)
        items = cal.get("items", []) if isinstance(cal, dict) else []
        return select_for_day(day, items, True)
    except Exception:
        return select_for_day(day, [], True)


@app.get("/api/dashboard")
def dashboard():
    cfg = load_config(); n = now_local()
    hd, hs = hebrew_date(n.date()); z, zs = zmanim(cfg, n.date())
    try:
        cal, cs = calendar(cfg, n.date(), 35)
    except Exception:
        cal = {"items": []}; cs = True
    ps = resolve_events(n.date(), z)
    future = [p for p in ps if p.get("time") and p["time"] > n.strftime("%H:%M")]
    anns = active_announcements()
    items = cal.get("items", []) if isinstance(cal, dict) else []
    event = next((x for x in items if x.get("date", "") >= n.date().isoformat() and x.get("category") in {"parashat", "holiday", "roshchodesh", "fast"}), None)
    try:
        h = select_for_day(n.date(), items, True)
    except Exception:
        h = None
    keys = [x for x in setting("display_zmanim", "").split(",") if x]
    times = z.get("times", {}) if isinstance(z, dict) else {}
    labels = {
        "alotHaShachar": "עלות", "misheyakir": "משיכיר", "sunrise": "הנץ",
        "sofZmanShmaMGA": "שמע מג״א", "sofZmanShma": "שמע גר״א", "sofZmanTfilla": "תפילה",
        "chatzot": "חצות", "minchaGedola": "מנחה גדולה", "minchaKetana": "מנחה קטנה",
        "plagHaMincha": "פלג", "sunset": "שקיעה", "tzeit7083deg": "צאת",
    }
    zstrip = [{"key": k, "label": labels.get(k, k), "time": fmt_ztime(times.get(k), cfg["timezone"])} for k in keys if times.get(k)]
    return {
        "server_time": n.isoformat(), "config": safe_cfg(), "hebrew_date": hd, "zmanim": z,
        "zmanim_strip": zstrip, "calendar_event": event, "prayers": ps,
        "next_prayer": future[0] if future else None, "announcements": anns,
        "halakha": h, "stale": hs or zs or cs,
        "main_slide_seconds": int(setting("main_slide_seconds", "30")),
    }


class Login(BaseModel):
    password: str


@app.post("/api/admin/login")
def login(body: Login):
    expected = _admin_password()
    if not expected or expected == "CHANGE-ME":
        raise HTTPException(503, "Définissez SYNACLOCK_ADMIN_PASSWORD dans Vercel")
    if not hmac.compare_digest(body.password, expected):
        raise HTTPException(401, "Mot de passe incorrect")
    expires = int(datetime.now(timezone.utc).timestamp()) + 43200
    token = _sign_session(expires)
    response = JSONResponse({"ok": True})
    response.set_cookie(
        "synaclock_session", token, httponly=True, samesite="strict",
        secure=os.getenv("VERCEL") == "1", max_age=43200,
    )
    return response


@app.post("/api/admin/logout")
def logout():
    response = JSONResponse({"ok": True})
    response.delete_cookie("synaclock_session")
    return response


@app.get("/api/admin/me")
def me(request: Request):
    auth(request)
    return {"authenticated": True}


@app.get("/api/admin/announcements")
def admin_announcements(request: Request):
    auth(request)
    rows = [r for r in list_all("announcements") if r.get("display_mode", "card") in {"card", "fullscreen"}]
    rows.sort(key=lambda x: (str(x.get("starts_at", "")), int(x.get("id", 0)) if str(x.get("id", "")).isdigit() else 0), reverse=True)
    return rows


class AnnouncementIn(BaseModel):
    title: str
    content: str = ""
    starts_at: str
    ends_at: str
    priority: int = 0
    active: bool = True
    display_mode: str = "card"
    duration: int = 12


def validate_content(x: AnnouncementIn):
    if not x.title.strip():
        raise HTTPException(422, "Le titre est obligatoire")
    if len(x.title) > 120 or len(x.content) > 2000:
        raise HTTPException(422, "Contenu trop long")
    try:
        start = datetime.fromisoformat(x.starts_at)
        end = datetime.fromisoformat(x.ends_at)
    except ValueError:
        raise HTTPException(422, "Dates invalides")
    if end <= start:
        raise HTTPException(422, "La fin doit être après le début")
    if x.display_mode not in {"card", "fullscreen"}:
        raise HTTPException(422, "Mode d'affichage invalide")
    if not 5 <= x.duration <= 120:
        raise HTTPException(422, "Durée entre 5 et 120 secondes")


def announcement_payload(x: AnnouncementIn):
    return {
        "title": x.title.strip(),
        "content": x.content.strip(),
        "starts_at": x.starts_at,
        "ends_at": x.ends_at,
        "priority": max(0, min(x.priority, 10)),
        "active": bool(x.active),
        "display_mode": x.display_mode,
        "duration": x.duration,
    }


@app.post("/api/admin/announcements")
def create_announcement(body: AnnouncementIn, request: Request):
    auth(request)
    validate_content(body)
    payload = announcement_payload(body)
    payload["created_at"] = datetime.now(timezone.utc).isoformat()
    return {"id": create("announcements", payload)}


@app.put("/api/admin/announcements/{item_id}")
def update_announcement(item_id: str, body: AnnouncementIn, request: Request):
    auth(request)
    validate_content(body)
    if not update("announcements", item_id, announcement_payload(body)):
        raise HTTPException(404, "Contenu introuvable")
    return {"ok": True}


@app.delete("/api/admin/announcements/{item_id}")
def delete_announcement(item_id: str, request: Request):
    auth(request)
    if not delete("announcements", item_id):
        raise HTTPException(404, "Contenu introuvable")
    return {"ok": True}


@app.get("/api/admin/schedule")
def get_schedule(request: Request):
    auth(request)
    rows = list_all("schedule_events")
    rows.sort(key=lambda x: (int(x.get("sort_order", 0)), int(x.get("id", 0)) if str(x.get("id", "")).isdigit() else 0))
    return rows


class ScheduleIn(BaseModel):
    name: str
    event_type: str = "office"
    weekdays: list[int]
    time_mode: str = "fixed"
    fixed_time: str | None = None
    base_zman: str | None = None
    offset_minutes: int = 0
    note: str = ""
    active: bool = True
    sort_order: int = 0


def validate_schedule(x: ScheduleIn):
    if not x.name.strip():
        raise HTTPException(422, "Nom obligatoire")
    if not x.weekdays or any(d < 0 or d > 6 for d in x.weekdays):
        raise HTTPException(422, "Choisissez au moins un jour")
    if x.time_mode not in {"fixed", "zman"}:
        raise HTTPException(422, "Mode horaire invalide")
    if x.time_mode == "fixed" and not re.match(r"^([01]\d|2[0-3]):[0-5]\d$", x.fixed_time or ""):
        raise HTTPException(422, "Heure HH:MM invalide")
    if x.time_mode == "zman" and not x.base_zman:
        raise HTTPException(422, "Choisissez un zman")


def schedule_payload(x: ScheduleIn):
    return {
        "name": x.name.strip(), "event_type": x.event_type,
        "weekdays": ",".join(map(str, sorted(set(x.weekdays)))), "time_mode": x.time_mode,
        "fixed_time": x.fixed_time, "base_zman": x.base_zman, "offset_minutes": x.offset_minutes,
        "note": x.note.strip(), "active": bool(x.active), "sort_order": x.sort_order,
    }


@app.post("/api/admin/schedule")
def add_schedule(body: ScheduleIn, request: Request):
    auth(request); validate_schedule(body)
    return {"id": create("schedule_events", schedule_payload(body))}


@app.put("/api/admin/schedule/{item_id}")
def edit_schedule(item_id: str, body: ScheduleIn, request: Request):
    auth(request); validate_schedule(body)
    if not update("schedule_events", item_id, schedule_payload(body)):
        raise HTTPException(404, "Événement introuvable")
    return {"ok": True}


@app.delete("/api/admin/schedule/{item_id}")
def del_schedule(item_id: str, request: Request):
    auth(request)
    if not delete("schedule_events", item_id):
        raise HTTPException(404, "Événement introuvable")
    return {"ok": True}


@app.get("/api/admin/settings")
def get_settings(request: Request):
    auth(request)
    return {
        "display_zmanim": setting("display_zmanim"),
        "poster_subtitle": setting("poster_subtitle"),
        "main_slide_seconds": setting("main_slide_seconds"),
    }


class SettingsIn(BaseModel):
    display_zmanim: list[str]
    poster_subtitle: str = ""
    main_slide_seconds: int = 30


@app.put("/api/admin/settings")
def put_settings(body: SettingsIn, request: Request):
    auth(request)
    set_setting("display_zmanim", ",".join(body.display_zmanim))
    set_setting("poster_subtitle", body.poster_subtitle[:120])
    set_setting("main_slide_seconds", str(max(10, min(body.main_slide_seconds, 180))))
    return {"ok": True}


@app.get("/api/admin/shabbat-preview")
def shabbat_preview(request: Request):
    auth(request); cfg = load_config(); today = now_local().date()
    delta = (4 - today.weekday()) % 7; friday = today + timedelta(days=delta); saturday = friday + timedelta(days=1)
    cal, _ = calendar(cfg, friday, 2); items = cal.get("items", []) if isinstance(cal, dict) else []
    candle = next((x.get("date", "") for x in items if x.get("category") == "candles"), None)
    havdalah = next((x.get("date", "") for x in items if x.get("category") == "havdalah"), None)
    parasha = next((x.get("title", "") for x in items if x.get("category") == "parashat"), None)
    zf, _ = zmanim(cfg, friday); zs, _ = zmanim(cfg, saturday)
    return {
        "friday": friday.isoformat(), "saturday": saturday.isoformat(), "parasha": parasha or "",
        "candle": fmt_ztime(candle, cfg["timezone"]), "havdalah": fmt_ztime(havdalah, cfg["timezone"]),
        "friday_events": resolve_events(friday, zf), "saturday_events": resolve_events(saturday, zs),
        "synagogue_name": cfg.get("synagogue_name", "SynaClock"), "city": cfg.get("city", ""),
        "subtitle": setting("poster_subtitle"),
    }


class ShabbatProgramIn(BaseModel):
    friday_date: str
    saturday_date: str
    friday: list[dict] = []
    saturday: list[dict] = []


def _clean_poster_rows(rows):
    out = []
    for event in rows[:30]:
        tm = str(event.get("time") or "").strip()
        if tm and not re.match(r"^([01]?\d|2[0-3])(?::|h)[0-5]\d$", tm):
            raise HTTPException(422, f"Heure invalide : {tm}")
        if "h" in tm:
            tm = tm.replace("h", ":", 1)
        out.append({
            "time": tm, "name": str(event.get("name") or "")[:180].strip(),
            "note": str(event.get("note") or "")[:500].strip(),
            "icons": [str(x)[:20] for x in (event.get("icons") or [])[:8]],
        })
    return out


@app.post("/api/admin/shabbat-program")
def save_shabbat_program(body: ShabbatProgramIn, request: Request):
    auth(request)
    try:
        friday = date.fromisoformat(body.friday_date); saturday = date.fromisoformat(body.saturday_date)
    except ValueError:
        raise HTTPException(422, "Dates de Chabbat invalides")
    if saturday != friday + timedelta(days=1):
        raise HTTPException(422, "Le samedi doit suivre le vendredi")
    payload = {"friday": _clean_poster_rows(body.friday), "saturday": _clean_poster_rows(body.saturday)}
    put_shabbat(friday.isoformat(), saturday.isoformat(), payload)
    return {"ok": True, "friday": friday.isoformat(), "saturday": saturday.isoformat()}
<<<<<<< HEAD
=======


# Media library: files hosted by Cloudinary, metadata persisted in Firestore.
def _media_origin(request: Request):
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") != str(request.base_url).rstrip("/"):
        raise HTTPException(403, "Origine non autorisée")


def _cloudinary_config():
    keys = [os.getenv(k) for k in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY", "CLOUDINARY_API_SECRET")]
    if not all(keys):
        raise HTTPException(503, "Configurez Cloudinary dans les variables Vercel")
    cloudinary.config(cloud_name=keys[0], api_key=keys[1], api_secret=keys[2], secure=True)


def _media_public():
    result = [x for x in list_all("media_images") if x.get("active", True)]
    return sorted(result, key=lambda x: (int(x.get("sort_order", 0)), str(x.get("id"))))


@app.get("/api/media/slides")
def media_slides():
    return _media_public()


@app.get("/api/admin/media")
def media_admin(request: Request):
    auth(request)
    return sorted(list_all("media_images"), key=lambda x: (int(x.get("sort_order", 0)), str(x.get("id"))))


@app.post("/api/admin/media")
def media_upload(request: Request, file: UploadFile = File(...)):
    auth(request)
    _media_origin(request)
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(422, "Formats autorisés : JPG, PNG, WEBP")
    payload = file.file.read(5 * 1024 * 1024 + 1)
    if len(payload) > 5 * 1024 * 1024:
        raise HTTPException(413, "Taille maximale : 5 Mo")
    # Check actual file signatures; don't trust the browser-supplied MIME type.
    valid = (payload.startswith(b"\xff\xd8\xff") or
             payload.startswith(b"\x89PNG\r\n\x1a\n") or
             (payload.startswith(b"RIFF") and payload[8:12] == b"WEBP"))
    if not valid:
        raise HTTPException(422, "Fichier image invalide")
    _cloudinary_config()
    try:
        result = cloudinary.uploader.upload(payload, folder="synaclock/slides", resource_type="image")
    except Exception as exc:
        raise HTTPException(502, "Échec de l'envoi vers Cloudinary") from exc
    row = {"title": (Path(file.filename or "image").stem[:100]),
           "image_url": result["secure_url"], "public_id": result["public_id"],
           "duration": 12, "sort_order": 0, "active": True,
           "created_at": datetime.now(timezone.utc).isoformat()}
    try:
        id_ = create("media_images", row)
    except Exception:
        cloudinary.uploader.destroy(result["public_id"], resource_type="image")
        raise
    return {**row, "id": id_}


class MediaEdit(BaseModel):
    title: str
    duration: int = 12
    sort_order: int = 0
    active: bool = True


@app.put("/api/admin/media/{media_id}")
def media_update(media_id: str, body: MediaEdit, request: Request):
    auth(request)
    _media_origin(request)
    if not 5 <= body.duration <= 120 or len(body.title) > 100 or not body.title.strip():
        raise HTTPException(422, "Titre ou durée invalide (5–120 secondes)")
    if not update("media_images", media_id, body.model_dump()):
        raise HTTPException(404, "Image introuvable")
    return {"ok": True}


@app.delete("/api/admin/media/{media_id}")
def media_delete(media_id: str, request: Request):
    auth(request)
    _media_origin(request)
    item = get("media_images", media_id)
    if not item:
        raise HTTPException(404, "Image introuvable")
    _cloudinary_config()
    try:
        result = cloudinary.uploader.destroy(item["public_id"], resource_type="image", invalidate=True)
        if result.get("result") not in ("ok", "not found"):
            raise ValueError("suppression non confirmée")
    except Exception as exc:
        raise HTTPException(502, "Impossible de supprimer l'image chez Cloudinary") from exc
    delete("media_images", media_id)
    return {"ok": True}
>>>>>>> 91b0023 (V3)
