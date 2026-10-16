# SynaClock — Mise à jour bleu ciel / blanc

- Tableau public et administration : nouvelle palette bleu ciel, blanc, bleu profond.
- Slides image : arrière-plan doux reprenant la photo (flou), carte claire, ombre, image entière préservée avec `object-fit: contain`.
- Vidéo Fire Stick : miniature réduite à 18×12 px et opacité 0,015, **non masquée en `display:none`** pour préserver les chances de lecture continue sur Silk. Ceci reste expérimental et n’empêche pas forcément la veille Vega OS.
- Horloge : calcul de l'heure affichée selon le fuseau `SYNAGOGUE_TIMEZONE`, indépendamment du fuseau local de Silk. Le décompte du prochain office se base désormais sur les heures/minutes locales de la synagogue.

## Déploiement
1. Conserver et vérifier les variables d'environnement existantes dans Vercel.
2. Vérifier la variable `SYNAGOGUE_TIMEZONE` (par exemple `Europe/Paris`, **pas** un décalage fixe UTC+1, car l'heure d'été change).
3. Envoyer les fichiers modifiés à GitHub puis redéployer Vercel.
4. Comparer sur l'écran TV l'horloge, les zmanim et les horaires d'office. Les horaires **fixes** enregistrés dans l'admin ne sont volontairement **pas décalés automatiquement**. Si ceux-ci sont décalés d'une heure, corriger leur saisie ou le fuseau configuré.
5. Tester 15 min puis plusieurs heures pour la veille.

## Note
Ce code a été vérifié syntaxiquement, pas testé avec votre Fire Stick, Vercel ou vos horaires en production.
