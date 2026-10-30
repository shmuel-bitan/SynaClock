# Déploiement Vercel — V4.4 (correctif 404)

1. Déployer **le contenu** de ce dossier à la racine du dépôt GitHub (pas le dossier parent).
2. Dans Vercel > Project > Settings > Build and Deployment, vérifier Root Directory = `./` ou vide et Framework Preset = Other (détection Python).
3. Vérifier que la branche Production de Vercel correspond à la branche poussée sur GitHub.
4. Après redeploy, ouvrir `/`, `/admin`, et `/api/health`.
5. Si 404 Vercel persiste, consulter Deployments > dernier déploiement > Build Logs et vérifier qu'une Python Function `api/index.py` apparaît ; sinon c'est un mauvais dossier ou une mauvaise branche.
6. Si FUNCTION_INVOCATION_FAILED / 500, consulter Runtime Logs (imports, variables d'environnement, initialisation Firestore).

Correction : la destination rewrite doit être `/api/index` (sans `.py`). Le chemin public reste transmis via le paramètre interne à la fonction ASGI.
