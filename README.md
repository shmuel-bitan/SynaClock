# SynaClock

SynaClock est un panneau d’information pour synagogue : horaires, zmanim, calendrier hébraïque, halakha du jour, annonces, slides et générateur d’affiche de Chabbat.

## Architecture

- FastAPI
- Cloud Firestore pour les données persistantes
- Hebcal pour calendrier/zmanim
- HTML/CSS/JavaScript sans framework
- Déploiement prévu sur Vercel

## Test local

Créer un environnement Python, installer `requirements.txt`, puis définir :

```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS="$HOME\Downloads\s.json"
$env:SYNACLOCK_ADMIN_PASSWORD="votre-mot-de-passe"
$env:SYNACLOCK_SESSION_SECRET="une-longue-cle-secrete"
$env:SYNAGOGUE_NAME="Votre synagogue"
$env:SYNAGOGUE_CITY="Paris"
$env:SYNAGOGUE_LATITUDE="48.8566"
$env:SYNAGOGUE_LONGITUDE="2.3522"
$env:SYNAGOGUE_TIMEZONE="Europe/Paris"
$env:SYNAGOGUE_ISRAEL="false"
uvicorn app.main:app --reload
```

Puis ouvrir :

- écran : http://127.0.0.1:8000
- admin : http://127.0.0.1:8000/admin

## Important

Ne jamais committer `s.json`, un compte de service Firebase, `.env` ou `config.json`.

Les images d’annonces ont volontairement été supprimées de cette version : les annonces sont soit des cartes, soit des slides texte. Le générateur d’affiche Chabbat reste local dans le navigateur et exporte son PNG sans stockage cloud.

## Mise à niveau depuis la V4

Si vous décompressez ce ZIP dans un projet existant, gardez votre fichier `app/static/shabbat-template-clean.png` (et vos éventuelles polices `app/static/fonts/`). Lancez ensuite `./cleanup_legacy.ps1` dans PowerShell pour supprimer les anciens modules de code SQLite restés dans le dossier.
