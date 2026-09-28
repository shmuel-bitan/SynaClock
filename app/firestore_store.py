import json
import os
import time
import hashlib
import uuid
from datetime import datetime, timezone
from functools import lru_cache

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError as exc:  # pragma: no cover - clearer startup error
    firebase_admin = None
    credentials = firestore = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None

DEFAULT_SETTINGS = {
    "display_zmanim": "sunrise,sofZmanShma,sofZmanTfilla,chatzot,sunset,tzeit7083deg",
    "poster_subtitle": "La synagogue tunisienne",
    "main_slide_seconds": "30",
}


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _credential_from_env():
    raw = _env("FIREBASE_SERVICE_ACCOUNT_JSON")
    if raw:
        try:
            info = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON n'est pas un JSON valide") from exc
        return credentials.Certificate(info)

    project_id = _env("FIREBASE_PROJECT_ID")
    client_email = _env("FIREBASE_CLIENT_EMAIL")
    private_key = _env("FIREBASE_PRIVATE_KEY")
    if project_id and client_email and private_key:
        info = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": _env("FIREBASE_PRIVATE_KEY_ID", "synaclock"),
            "private_key": private_key.replace("\\n", "\n"),
            "client_email": client_email,
            "client_id": _env("FIREBASE_CLIENT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": _env("FIREBASE_CLIENT_CERT_URL", ""),
        }
        return credentials.Certificate(info)

    # Works with GOOGLE_APPLICATION_CREDENTIALS locally if configured.
    return credentials.ApplicationDefault()


@lru_cache(maxsize=1)
def app_instance():
    if firebase_admin is None:
        raise RuntimeError("firebase-admin n'est pas installé. Lancez pip install -r requirements.txt") from _IMPORT_ERROR
    if firebase_admin._apps:
        return firebase_admin.get_app()
    try:
        return firebase_admin.initialize_app(_credential_from_env())
    except Exception as exc:
        raise RuntimeError(
            "Firebase Admin non configuré. Définissez FIREBASE_SERVICE_ACCOUNT_JSON ou "
            "FIREBASE_PROJECT_ID/FIREBASE_CLIENT_EMAIL/FIREBASE_PRIVATE_KEY dans Vercel."
        ) from exc


@lru_cache(maxsize=1)
def db():
    app_instance()
    return firestore.client()


def init_store():
    database = db()
    ref = database.collection("settings").document("main")
    snap = ref.get()
    if not snap.exists:
        ref.set(DEFAULT_SETTINGS)
    else:
        current = snap.to_dict() or {}
        missing = {k: v for k, v in DEFAULT_SETTINGS.items() if k not in current}
        if missing:
            ref.set(missing, merge=True)

    # Keep the first-run behaviour from the SQLite version.
    docs = list(database.collection("schedule_events").limit(1).stream())
    if not docs:
        create("schedule_events", {
            "name": "שחרית / Chaharit",
            "event_type": "office",
            "weekdays": "0,1,2,3,4,5,6",
            "time_mode": "fixed",
            "fixed_time": "08:00",
            "base_zman": None,
            "offset_minutes": 0,
            "note": "",
            "active": True,
            "sort_order": 0,
        })


def _numeric_id(collection: str) -> str:
    # 13-digit millisecond IDs remain exactly representable by JS Number and keep
    # the current admin.html working without UI changes.
    base = int(time.time() * 1000)
    col = db().collection(collection)
    for offset in range(1000):
        candidate = str(base + offset)
        if not col.document(candidate).get().exists:
            return candidate
    return str(int(time.time() * 1000)) + str(uuid.uuid4().int % 1000)


def create(collection: str, data: dict, doc_id: str | None = None) -> int | str:
    doc_id = doc_id or _numeric_id(collection)
    payload = dict(data)
    db().collection(collection).document(str(doc_id)).set(payload)
    return int(doc_id) if str(doc_id).isdigit() and len(str(doc_id)) <= 15 else doc_id


def get(collection: str, doc_id) -> dict | None:
    snap = db().collection(collection).document(str(doc_id)).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data["id"] = int(snap.id) if snap.id.isdigit() and len(snap.id) <= 15 else snap.id
    return data


def list_all(collection: str) -> list[dict]:
    out = []
    for snap in db().collection(collection).stream():
        data = snap.to_dict() or {}
        data["id"] = int(snap.id) if snap.id.isdigit() and len(snap.id) <= 15 else snap.id
        out.append(data)
    return out


def update(collection: str, doc_id, data: dict):
    ref = db().collection(collection).document(str(doc_id))
    if not ref.get().exists:
        return False
    ref.update(dict(data))
    return True


def delete(collection: str, doc_id):
    ref = db().collection(collection).document(str(doc_id))
    if not ref.get().exists:
        return False
    ref.delete()
    return True


def setting(key: str, default: str = "") -> str:
    snap = db().collection("settings").document("main").get()
    if not snap.exists:
        return default
    value = (snap.to_dict() or {}).get(key, default)
    return str(value) if value is not None else default


def set_setting(key: str, value):
    db().collection("settings").document("main").set({key: value}, merge=True)


def get_shabbat(friday_date: str) -> dict | None:
    snap = db().collection("shabbat_programs").document(friday_date).get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data["id"] = snap.id
    return data


def put_shabbat(friday_date: str, saturday_date: str, payload: dict):
    db().collection("shabbat_programs").document(friday_date).set({
        "friday_date": friday_date,
        "saturday_date": saturday_date,
        "payload": payload,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


def cache_get(key: str):
    doc_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
    snap = db().collection("cache").document(doc_id).get()
    return (snap.to_dict() or {}).get("payload") if snap.exists else None


def cache_put(key: str, payload):
    doc_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
    db().collection("cache").document(doc_id).set({
        "cache_key": key,
        "payload": payload,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })

