# Lexique des champs d'un match

Chaque match est un JSON `{"result": {...}}` (voir `docs/match_example.json`, match réel 5651481606). Ce lexique liste les champs utiles pour le projet, le reste est du bruit.

## Niveau match (dans `result`)

| Champ | Rôle |
|---|---|
| `radiant_win` | Booléen. LE label à prédire (True = Radiant a gagné). |
| `duration` | Durée en secondes. Sert aux questions durées les plus longues/courtes par héros. |
| `start_time` | Timestamp Unix du début. Période des données : sept-oct 2020. |
| `lobby_type` | 7 = ranked. 100 % du dataset, rien à filtrer. |
| `game_mode` | 22 = All Pick (88,5 %), 3 = Random Draft (11,4 %), 2 = Captain's Mode (0,1 %). Aucun filtre décidé pour l'instant. |
| `human_players` | 10 partout. |
| `radiant_score` / `dire_score` | Kills totaux par camp. |
| `first_blood_time` | Seconde de la première mort. |
| `tower_status_radiant` / `tower_status_dire` et `barracks_status_radiant` / `barracks_status_dire` | Bitmasks des tours/casernes restantes en fin de partie. Contexte de fin de match, peu utilisé. |
| `picks_bans[]` | Le draft ordonné. Sous-champs : `is_pick` (True = pick, False = ban), `hero_id`, `team` (0 = Radiant, 1 = Dire), `order` (0-16, ordre chronologique). Sert aux tools de l'agent (que drafter maintenant, first picks) et aux questions de draft. |

## Niveau joueur (dans `players[10]`)

- `player_slot` : 0 à 4 = Radiant, 128 à 132 = Dire. Indique de quel côté un héros a joué.
- `hero_id` : identifiant du héros, à traduire en nom via `code/doracle/data/heroes.json`.
- `leaver_status` : 0 = match normal. Valeur >= 2 = abandon. LE critère d'exclusion du projet : un match avec un seul abandon est exclu (une win 4v5 ne reflète pas le draft).
- `kills` / `deaths` / `assists` : score du joueur.
- `level`, `gold_per_min`, `xp_per_min`, `last_hits`, `hero_damage`, `tower_damage` : performance du joueur, pas utilisée par le modèle.
- `account_id` : 4294967295 = joueur anonyme. Sans importance.

## Bruit à ignorer

- `ability_upgrades[]` (build de sorts, très verbeux), `item_*`, `backpack_*`, `scaled_*`, `gold`, `gold_spent`, `cluster`, `leagueid`, `flags`, `engine`, votes, `server_ip`/`server_port` (présents seulement parfois) : pas utilisés par le projet.
