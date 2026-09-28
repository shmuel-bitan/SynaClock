"""Migration facultative de l'ancienne data/synaclock.db vers Firestore.
Lancer une seule fois après avoir configuré les variables Firebase.
"""
import json
import sqlite3
from pathlib import Path
from app.firestore_store import db, init_store

DB = Path(__file__).resolve().parent.parent / "data" / "synaclock.db"
if not DB.exists():
    raise SystemExit(f"Ancienne base introuvable: {DB}")

init_store()
fire = db()
con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

def rows(table):
    try:
        return [dict(x) for x in con.execute(f"SELECT * FROM {table}").fetchall()]
    except sqlite3.OperationalError:
        return []

for item in rows("schedule_events"):
    doc_id = str(item.pop("id"))
    item["active"] = bool(item.get("active", 1))
    fire.collection("schedule_events").document(doc_id).set(item)

for item in rows("announcements"):
    doc_id = str(item.pop("id"))
    item["active"] = bool(item.get("active", 1))
    # Old /media URLs were local to the Raspberry/PC and cannot be migrated automatically.
    if str(item.get("media_path") or "").startswith("/media/"):
        item["media_path"] = None
    fire.collection("announcements").document(doc_id).set(item)

settings = {r["key"]: r["value"] for r in rows("settings")}
if settings:
    fire.collection("settings").document("main").set(settings, merge=True)

for item in rows("shabbat_programs"):
    payload = item.get("payload")
    try:
        payload = json.loads(payload) if isinstance(payload, str) else payload
    except Exception:
        payload = {"friday": [], "saturday": []}
    fire.collection("shabbat_programs").document(item["friday_date"]).set({
        "friday_date": item["friday_date"],
        "saturday_date": item["saturday_date"],
        "payload": payload,
        "updated_at": item.get("updated_at", ""),
    })

print("Migration terminée. Les anciennes images locales doivent être ré-uploadées depuis l'admin.")
