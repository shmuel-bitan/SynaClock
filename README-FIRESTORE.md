# SynaClock V4 — Firestore / Vercel

Cette version remplace SQLite par Cloud Firestore et les uploads locaux par Firebase Storage.
L'interface publique et l'admin restent les mêmes.

## Collections utilisées

- `schedule_events`
- `announcements`
- `shabbat_programs`
- `settings/main`
- `cache`

`data/halakhot.json` reste un fichier statique versionné dans le projet.

## Variables Vercel obligatoires

Copier les valeurs de `.env.example` dans Vercel > Project > Settings > Environment Variables.
Les secrets Firebase et le mot de passe admin ne doivent jamais être ajoutés à GitHub.

Firebase peut être configuré soit avec `FIREBASE_SERVICE_ACCOUNT_JSON`, soit avec :
`FIREBASE_PROJECT_ID`, `FIREBASE_CLIENT_EMAIL`, `FIREBASE_PRIVATE_KEY`.

Pour les images, configurer aussi `FIREBASE_STORAGE_BUCKET`.

## Mise à jour de l'écran

L'écran public recharge `/api/dashboard` toutes les 10 secondes. Une modification faite dans `/admin`
est donc visible sur l'écran au plus tard environ 10 secondes après l'enregistrement, sans redéploiement Vercel.
Un changement de code/design nécessite un nouveau déploiement et un rechargement du navigateur du stick.

## Démarrage local

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# définir les variables d'environnement Firebase
uvicorn app.main:app --reload
```

## Déploiement Vercel

Le fichier `app/main.py` expose directement une instance FastAPI nommée `app`, format reconnu par Vercel.
Après le push GitHub, importer le dépôt dans Vercel, renseigner les variables d'environnement et déployer.

## Ancienne base SQLite

`data/synaclock.db` n'est plus lue. Elle peut être conservée localement comme sauvegarde et est ignorée par Git.

## Important avant GitHub

`config.json` est maintenant ignoré par Git pour éviter de publier un ancien `admin_password` par erreur.
Utilisez `config.example.json` comme modèle local. Sur Vercel, mettez la configuration dans les variables d'environnement.

Pour Firestore, le backend utilise Firebase Admin : les règles Firestore peuvent donc rester fermées aux clients web.
