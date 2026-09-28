"""Legacy module kept only so an old import fails clearly.

SynaClock V4 stores persistent data in Cloud Firestore. New code must import
`app.firestore_store` instead of this module.
"""

def connect():
    raise RuntimeError("SQLite est désactivé dans SynaClock V4. Utilisez Firestore.")


def init_db():
    raise RuntimeError("SQLite est désactivé dans SynaClock V4. Utilisez init_store().")
