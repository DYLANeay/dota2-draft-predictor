# TODO : Molde Dotaklubb (IKT110, lab5 Dota 2)

Projet pour Molde Dotaklubb : implémenter la partie ML d'une page web de prédiction de drafts Dota 2, déployer la page complète, rendre un rapport PDF et présenter oralement.

## Livrables

- Zip final contenant : le rapport (PDF) + le code.
- Rapport : description technique et informelle, bullet lists, pas besoin d'être joli. Sert de cheat sheet pour la présentation. Template LaTeX dans `report/` (style arXiv).
- Présentation orale en 2 parties : technique (comment ça marche) + tournée vers Molde Dotaklubb (comment utiliser l'outil pour améliorer leur drafting).
- Le projet n'est livré qu'après la présentation orale. Deadline pas encore fixée.

## Ce qui est déjà là (ne pas réinventer)

- `code/` : framework fourni. App Flask + agent LLM (llm-interaction, DeepSeek) fonctionnels. UI de pick/ban (5 picks + 7 bans par équipe, Radiant/Dire) + boîte "Ask".
- README complet dedans : `uv sync`, `.env` avec `LLM_INTERACTION_API_KEY`, `uv run pytest`, `uv run dota-oracle`.
- `code/doracle/model.py` : HeroStats placeholder qui renvoie des valeurs aléatoires → la partie à remplacer par un vrai modèle entraîné.
- `code/doracle/tools.py` : tools existants = `resolve_hero`, `list_heroes`, `hero_stats` (branché sur le placeholder), `submit_answer` → à étendre.
- `code/doracle/heroes.py` + `code/doracle/data/heroes.json` : roster, alias de noms, correspondance hero id → nom.
- `report/` : template LaTeX (arxiv.sty, template.tex, references.bib).
- Les données ne sont PAS dans le repo : à télécharger.

## À faire

1. **Données**
   - Télécharger : https://www.dropbox.com/scl/fi/sf8tyklvcc8b9e3751jis/dota_games_final.zip?rlkey=bf05l2b2euy6c6ukobraqm5pt&st=izqh8n7i&dl=0
   - Format JSON spécifié sur https://wiki.teamfortress.com/wiki/WebAPI/GetMatchDetails
   - Filtrer les matchs et documenter inclusion/exclusion (question 1 du rapport).
   - id → nom via `code/doracle/data/heroes.json`.

2. **Modèle**
   - Algo parmi ceux vus en classe : Logistic Regression, Linear Regression, MLP 2 couches, ou Fortuna.
   - Implémentation perso valorisée ; sinon scikit-learn autorisé.
   - Définir features + hyper-paramètres (à documenter dans le rapport).
   - Remplacer le placeholder `code/doracle/model.py` par le vrai modèle entraîné.

3. **Tools de l'agent LLM**
   - Étendre `code/doracle/tools.py` pour couvrir les questions requises. Exemples attendus :
     - hero au plus haut winrate en ranked ;
     - meilleur hero en synergie avec le hero X ;
     - que drafter maintenant (contexte fourni par l'interface web) ;
     - que drafter en last pick.
   - L'agent doit s'appuyer sur les statistiques des données, PAS sur la connaissance du LLM (les données ne correspondent pas au Dota 2 moderne).
   - DeepSeek recommandé (pas obligatoire).
   - Lister les tools exposés au LLM et leur usage dans le rapport.

4. **Les 12 questions d'analyse (à répondre dans le rapport)**
   1. Quels matchs exclure/inclure pour l'analyse ?
   2. Hero le plus picked ?
   3. Hero au plus haut winrate ?
   4. Avantage à jouer Dire ou Radiant ?
   5. Hero avec le plus gros impact sur le game (définir "impact" soi-même) ?
   6. Hero avec les games les plus longues ?
   7. Hero avec les games les plus courtes ?
   8. Meilleure paire de heroes ?
   9. Hero le plus dur counter par un autre hero ?
   10. Meilleur hero s'il n'est pas countered par ses TOP 5 counters ?
   11. 2 heroes qu'une team peut first pick sans risque ?
   12. Comment Molde Dotaklubb peut utiliser la page web pour s'améliorer ?

5. **Critères de la webpage**
   - Assister le drafting, pas juste prédire le gagnant.
   - Proposer un hero similaire si le hero voulu est banni ou pris par l'ennemi.

6. **Rapport**
   - Contenu exigé : entraînement du modèle, features, hyper-paramètres ; liste des tools exposés au LLM et leur usage ; réponses aux 12 questions.
   - Style : bullets, technique et informel, pas de mise en page soignée.
   - Utiliser le template LaTeX `report/` (voir aussi report_outline.pdf sur Canvas).

7. **Présentation orale**
   - Partie 1 : technique (comment ça marche).
   - Partie 2 : Molde Dotaklubb (comment utiliser l'outil pour améliorer leur drafting).
   - Le rapport = cheat sheet de la présentation.

## Pièges / rappels

- Jamais d'hero IDs dans le rapport ni la présentation : toujours des noms de heroes.
- Stats des données ≠ connaissance LLM : l'agent répond depuis les données.
- Implémentation perso de l'algo compte positivement.
- Deadline pas encore fixée.
