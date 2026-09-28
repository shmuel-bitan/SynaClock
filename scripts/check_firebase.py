from app.firestore_store import db, init_store

init_store()
client = db()
client.collection("meta").document("healthcheck").set({"ok": True})
print("OK - connexion Firestore fonctionnelle")
