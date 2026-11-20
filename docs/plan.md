# Plan de travail : Molde Dotaklubb (IKT110, lab5 Dota 2)

Plan de travail de l'équipe. Le détail des tâches est dans `docs/TODO.md` ; ce document fixe qui fait quoi et dans quel ordre. Deadline pas encore fixée, le projet est livré après la présentation orale.

## Équipe

- Dylan (propriétaire du repo)
- Cem
- Simon

## Répartition

| Qui | Quoi | Statut |
|---|---|---|
| Dylan | ① données (extraire, filtrer, documenter inclusion/exclusion) + ② modèle ML (remplacer le placeholder `code/doracle/model.py`) | **confirmé** : c'est TOUT son périmètre |
| Cem | Présentation business (partie tournée vers Molde Dotaklubb) + feature webpage « hero similaire si banni/pris » (critère exigé par l'assignment) + ⑦ packaging/zip final | confirmé (présentation business) + **proposition pour le reste, à valider** |
| Simon | ③ tools de l'agent LLM + ④ les 12 questions d'analyse (elles partagent les mêmes stats que les tools) + lead sur ⑤ le rapport | **proposition, à valider** |
| Simon ou Cem | Présentation technique (Dylan ne la prend pas) | **proposition, à valider** |

- Dylan garde ①-② tout de suite, sans dépendre de personne ; son périmètre s'arrête là.
- ③ et suivantes dépendent de ①-②, mais c'est Dylan qui produit ces prérequis, pas l'inverse.
- ⚠️ Tout sauf Dylan-données/modèle et Cem-présentation-business = propositions à valider en équipe.

## Ordre de bataille

1. **Données** (Dylan) : zip de 7,6 Go déjà téléchargé ; extraire, filtrer les matchs, documenter inclusion/exclusion.
2. **Modèle ML** (Dylan) : Logistic Regression / Linear Regression / MLP 2 couches / Fortuna ; remplacer le placeholder `code/doracle/model.py`.
3. **Tools de l'agent LLM** (Simon ?) : expose les stats des données, pas la connaissance du LLM ; dépend de ①-②.
4. **12 questions d'analyse** (Simon ?) : dépend de ① prêt.
5. **Rapport** (co-rédaction, lead Simon ?) : template LaTeX dans `report/` ; tous contribuent à leurs sections (Dylan : entraînement/features/hyperparams ; Cem : sections usage club).
6. **Présentations** : business (Cem, confirmé) + technique (Simon ou Cem ?) ; le rapport sert de cheat sheet.
7. **Zip final + répétition** (Cem ?) : rapport PDF + code ; après la présentation orale.

- Dylan démarre ①-② tout de suite, sans attendre personne.
- ③ et au-delà démarrent dès que ①(-②) est prêt.
