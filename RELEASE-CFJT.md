# SynaClock — adaptation CFJT (30 octobre 2026)

## Modifications effectuées
- Palette blanc / bleu ciel sur écran TV et administration. Les valeurs sont provisoires : échantillon officiel CFJT non fourni.
- API `/api/dashboard` : `week_program`, calcul des événements du jour et des 6 jours suivants, incluant le samedi dès vendredi.
- Interface TV : horaires de demain et aperçu de la semaine entière, sans changement du panneau de gestion existant.
- Conservation de Firestore, Cloudinary, halakhot, annonces, génération de l'affiche de Chabbat, rotation des diapositives et vidéo anti-veille.

## À vérifier sur installation réelle
- Identifiants Firebase et Cloudinary dans les variables d'environnement (jamais dans le ZIP).
- Connexion au projet Firestore, temps de réponse Hebcal, horaires et fuseau réels du CFJT.
- Déploiement Vercel : configuration du point d'entrée ASGI et variables d'environnement ; aucun déploiement distant effectué.
- Anti-veille Fire TV : la vidéo muette ne garantit pas la désactivation de la veille du système.
- Rendu TV réel (dimensions, longueurs des noms, affiches) et couleurs exactes de la synagogue.
- Comportement des horaires passés : le prochain événement demeure limité au jour en cours.

## Démarrage local
`pip install -r requirements.txt` puis `uvicorn app.main:app --reload`. Voir `.env.example` et `README.md` pour les réglages requis.

- Ajout de `api/index.py` (export ASGI) et `vercel.json` (réécriture vers `/api`) ; configuration à valider sur un déploiement Vercel réel.
