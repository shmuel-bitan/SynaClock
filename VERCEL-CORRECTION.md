# Correctif Vercel — CFJT V4.3

## Origine de l'erreur
La V4.2 réécrivait toutes les URLs vers `/api`, si bien que FastAPI recevait
`/api` au lieu de `/`, `/admin` ou `/api/dashboard`, et renvoyait `{"detail":"Not Found"}`.

## Correctif
La règle `vercel.json` transmet maintenant le chemin public d'origine à
`api/index.py`, qui le restaure avant de transmettre la requête à FastAPI.

## Déploiement
Remplacer le contenu du dépôt GitHub par celui de ce ZIP **à la racine** (les
fichiers `vercel.json`, `requirements.txt`, les répertoires `app/`, `api/` doivent
être à la racine). Ne pas inclure de dossier parent supplémentaire.
Pousser les modifications sur la branche reliée à Vercel.
Dans Vercel > Project > Settings > Build and Deployment : Root Directory doit
pointer sur le dossier contenant `vercel.json` (en général `./`). Vérifier
également les variables d'environnement Firebase et Cloudinary.
Tester / puis /admin, /api/health et /static/index.html.

Si le problème persiste, transmettre l'URL Vercel et les journaux du déploiement.
