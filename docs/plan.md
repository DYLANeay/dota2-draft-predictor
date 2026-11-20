# Plan de travail : Molde Dotaklubb (IKT110, lab5 Dota 2)

Plan de travail de l'équipe. Le détail des tâches est dans `docs/TODO.md` ; ce document fixe qui fait quoi et dans quel ordre. Deadline pas encore fixée, le projet est livré après la présentation orale.

## Équipe

- Dylan (propriétaire du repo)
- Cem
- Simon

## Répartition

| Qui | Quoi | Statut |
|---|---|---|
| Dylan | ① Données, ② modèle ML, ③ tools de l'agent (chemin critique) | confirmé |
| Cem | Présentation business (partie tournée vers Molde Dotaklubb : comment utiliser la page web pour améliorer leur drafting) | confirmé |
| Simon | ④ Les 12 questions d'analyse + co-rédaction du rapport | **proposition, à valider** |
| Dylan | Présentation technique (il connaît le code) | **proposition, à valider** |

- Dylan prend les premières tâches du chemin critique pour ne dépendre de personne en attendant.
- ⚠️ Répartition Simon + présentation technique = propositions, à valider en équipe.

## Ordre de bataille

1. **Données** (Dylan) : zip de 7,6 Go déjà téléchargé ; extraire, filtrer les matchs, documenter inclusion/exclusion.
2. **Modèle ML** (Dylan) : Logistic Regression / Linear Regression / MLP 2 couches / Fortuna ; remplacer le placeholder `code/doracle/model.py`.
3. **Tools de l'agent LLM** (Dylan) : exposer les stats des données, pas la connaissance du LLM.
4. **12 questions d'analyse** (Simon ?) : dépend de ① prêt.
5. **Rapport** (co-rédaction) : template LaTeX dans `report/` ; dépend de ①-④.
6. **Présentations** : technique (Dylan ?) + business (Cem) ; le rapport sert de cheat sheet.
7. **Zip final + répétition** : rapport PDF + code ; après la présentation orale.

- Dylan démarre ①-③ tout de suite, sans attendre personne.
- ④ et au-delà peuvent démarrer dès que ① est prêt.
