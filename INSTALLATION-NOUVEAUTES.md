# SynaClock : images, affiches et affichage Fire TV

## Configuration gratuite des images

1. Créer un compte sur https://cloudinary.com/ et récupérer `Cloud name`, `API Key`, `API Secret` dans la console Cloudinary.
2. Dans Vercel > Projet SynaClock > Settings > Environment Variables, ajouter :
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Conserver les variables `FIREBASE_*`, `SYNACLOCK_ADMIN_PASSWORD` et `SYNACLOCK_SESSION_SECRET` existantes.
4. Envoyer les fichiers de cette archive dans la branche déployée, puis redéployer. Les dépendances `cloudinary` et `python-multipart` sont ajoutées à requirements.txt.
5. Ouvrir `/admin`, se connecter, puis onglet **Images**. Importer une image JPG/PNG/WEBP de 5 Mo maximum. Modifier la durée (5 à 120 s), l'ordre et l'activation ; cliquer sur Enregistrer.
6. Dans **Affiche Chabbat**, choisir l’affiche qui apparaît à gauche sur l’écran. « Importer l’affiche jointe » ajoute l’exemple fourni ; une image envoyée avec le type « Affiche de Chabbat » est sélectionnée automatiquement.
7. Les images actives, y compris l’affiche sélectionnée, apparaissent aussi dans la rotation plein écran.

Les fichiers sont chez Cloudinary, les métadonnées dans la collection Firestore `media_images`. Aucun Firebase Storage requis. L'offre gratuite Cloudinary est soumise aux quotas en vigueur.

## Affiche Chabbat

De petits coins filigranés dorés et des étoiles sont ajoutés directement au dessin canvas : l'aperçu ET le PNG exporté les incluent. La mise en page existante reste inchangée.

## Affichage Fire TV

La page web ne lance plus de vidéo de diagnostic ni de widget anti-veille. L’affichage sur Fire TV passe par l’application Vega, qui ouvre le site en plein écran. Le projet Vega et son lecteur audio natif sont maintenus séparément du dépôt web. Après un redémarrage du Stick, l’application doit être relancée manuellement.

## Limitations / sécurité

- Ne jamais mettre `CLOUDINARY_API_SECRET` dans GitHub ni dans le HTML. Seule l'API FastAPI authentifiée traite les uploads et suppressions.
- L'authentification utilise le cookie de session administrateur existant ; un contrôle d'origine est ajouté aux nouvelles opérations modifiantes.
- Tests automatiques de syntaxe Python/JavaScript réalisés. Un test réel de Cloudinary/Firestore, du navigateur Silk et du rendu de l'affiche reste nécessaire après déploiement.
- Vercel peut imposer des limites sur la taille des requêtes et leur durée : garder les images compressées sous 4 Mo en pratique, même si le code accepte 5 Mo.
