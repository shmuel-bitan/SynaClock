# SynaClock — adaptation CFJT (2 novembre 2026)

## Modifications effectuées
- Palette harmonisée sur l’écran TV, l’administration et l’affiche à partir du bandeau CFJT fourni : bleu principal #0068B0, fond clair et accent or.
- API `/api/dashboard` : `week_program`, calcul des événements du jour et des 6 jours suivants, incluant le samedi dès vendredi.
- Interface TV : horaires agrandis et liste compacte des prochains événements de la semaine, sans grille de calendrier.
- Bloc gauche remplacé par l’affiche de Chabbat sélectionnable dans l’administration ; les affiches actives restent aussi dans la rotation plein écran.
- Nouveau fond panoramique inspiré de la maison tunisienne et de la porte bleue de l’affiche fournie, avec logo CFJT dans l’en-tête.
- Conservation de Firestore, Cloudinary, halakhot, annonces, génération de l'affiche de Chabbat et rotation des diapositives. Les diagnostics anti-veille web sont retirés ; l'affichage Fire TV utilise l'application Vega.

## À vérifier sur installation réelle
- Identifiants Firebase et Cloudinary dans les variables d'environnement (jamais dans le ZIP).
- Connexion au projet Firestore, temps de réponse Hebcal, horaires et fuseau réels du CFJT.
- Déploiement Vercel : configuration du point d'entrée ASGI et variables d'environnement ; aucun déploiement distant effectué.
- Fonctionnement sur le Firestick : l’utilisateur confirme que l’application Vega fonctionne ; après redémarrage, elle doit être relancée manuellement.
- Rendu TV réel (dimensions, longueurs des noms et affiches) à confirmer dans la salle.
- Dans `/admin` > **Affiche Chabbat**, importer l’affiche jointe ou choisir une affiche active ; une affiche peut aussi être envoyée depuis le générateur avec « Ajouter l’affiche créée au diaporama ».
- Comportement des horaires passés : le prochain événement demeure limité au jour en cours.

## Démarrage local
`pip install -r requirements.txt` puis `uvicorn app.main:app --reload`. Voir `.env.example` et `README.md` pour les réglages requis.

- Ajout de `api/index.py` (export ASGI) et `vercel.json` (réécriture vers `/api`) ; configuration à valider sur un déploiement Vercel réel.
