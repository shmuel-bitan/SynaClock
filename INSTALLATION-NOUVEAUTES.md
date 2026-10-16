# SynaClock : upload d'images, affiches et test de veille

## Configuration gratuite des images

1. Créer un compte sur https://cloudinary.com/ et récupérer `Cloud name`, `API Key`, `API Secret` dans la console Cloudinary.
2. Dans Vercel > Projet SynaClock > Settings > Environment Variables, ajouter :
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Conserver les variables `FIREBASE_*`, `SYNACLOCK_ADMIN_PASSWORD` et `SYNACLOCK_SESSION_SECRET` existantes.
4. Envoyer les fichiers de cette archive dans la branche déployée, puis redéployer. Les dépendances `cloudinary` et `python-multipart` sont ajoutées à requirements.txt.
5. Ouvrir `/admin`, se connecter, puis onglet **Images**. Importer une image JPG/PNG/WEBP de 5 Mo maximum. Modifier la durée (5 à 120 s), l'ordre et l'activation ; cliquer sur Enregistrer.
6. Sur l'écran `/`, les images apparaîtront en plein écran, entre les passages de l'écran principal, avec les annonces textuelles déjà présentes.

Les fichiers sont chez Cloudinary, les métadonnées dans la collection Firestore `media_images`. Aucun Firebase Storage requis. L'offre gratuite Cloudinary est soumise aux quotas en vigueur.

## Affiche Chabbat

De petits coins filigranés dorés et des étoiles sont ajoutés directement au dessin canvas : l'aperçu ET le PNG exporté les incluent. La mise en page existante reste inchangée.

## Vidéo anti-veille Fire Stick HD / Amazon Silk

Une vidéo MP4 muette animée de quatre secondes est fournie et jouée en boucle en haut à droite sur `/`. Cette méthode est un **test**, non une garantie contre la veille de Vega OS. Sur le téléviseur, ouvrir `/` avec Amazon Silk, toucher la page si la lecture automatique est bloquée, puis ne rien faire pendant au moins 15 minutes. Vérifier si la veille revient. Le système peut suspendre Silk même lorsque la vidéo tourne.

## Limitations / sécurité

- Ne jamais mettre `CLOUDINARY_API_SECRET` dans GitHub ni dans le HTML. Seule l'API FastAPI authentifiée traite les uploads et suppressions.
- L'authentification utilise le cookie de session administrateur existant ; un contrôle d'origine est ajouté aux nouvelles opérations modifiantes.
- Tests automatiques de syntaxe Python/JavaScript réalisés. Un test réel de Cloudinary/Firestore, du navigateur Silk et du rendu de l'affiche reste nécessaire après déploiement.
- Vercel peut imposer des limites sur la taille des requêtes et leur durée : garder les images compressées sous 4 Mo en pratique, même si le code accepte 5 Mo.
