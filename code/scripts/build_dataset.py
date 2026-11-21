# /// script
# requires-python = ">=3.12"
# dependencies = ["tqdm>=4.66"]
# ///
# Run from code/: uv run scripts/build_dataset.py [--limit N]
#
# Stream data/dota_games_final.zip (NEVER extracted) and build:
#   - code/doracle/data/hero_stats.json: hero/pair/first-pick statistics (committable)
#   - data/processed/matches.csv: one row per included match (gitignored)
#   - data/processed/exclusion_report.json: global inclusion/exclusion counts (gitignored)

import argparse
import json
import zipfile
from pathlib import Path

from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
ZIP_PATH = REPO_ROOT / "data" / "dota_games_final.zip"
HEROES_JSON_PATH = REPO_ROOT / "code" / "doracle" / "data" / "heroes.json"
HERO_STATS_PATH = REPO_ROOT / "code" / "doracle" / "data" / "hero_stats.json"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
CSV_PATH = PROCESSED_DIR / "matches.csv"
EXCLUSION_REPORT_PATH = PROCESSED_DIR / "exclusion_report.json"

# radiant and dire are each 5 heroes, and the last column is 1 if radiant won, else 0
# genre real vs barça finalement
CSV_HEADER = (
    "radiant_1,radiant_2,radiant_3,radiant_4,radiant_5,"
    "dire_1,dire_2,dire_3,dire_4,dire_5,radiant_win"
)

EXCLUSION_REASONS = ("leaver", "human_players", "invalid_heroes", "match_id_mismatch")


# parser, on peut ajouter des arguments pour limiter le nombre de matchs à traiter, etc.
def parse_args():
    parser = argparse.ArgumentParser(
        description="Build the Dota 2 draft dataset from the streamed match archive"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="process only the first N archive entries (sample run)",
    )
    return parser.parse_args()


# gabarit de stats pour un héros, utilisé pour initialiser les entrées dans le dictionnaire heroes
def new_hero_stats():
    return {
        "picks": 0,
        "wins": 0,
        "radiant_picks": 0,
        "radiant_wins": 0,
        "dire_picks": 0,
        "dire_wins": 0,
        "duration_sum": 0,
        "duration_count": 0,
    }


# notation un peu weird mais : 0 à 4 pour radiant, 128 à 132 pour dire, sinon invalide
def split_teams(players):
    """Return (radiant_heroes, dire_heroes), or None if heroes/slots do not form a valid 5v5."""
    radiant, dire = [], []
    for player in players:
        hero_id = player.get("hero_id", 0)
        if not hero_id:
            return None
        slot = player.get("player_slot", -1)
        if 0 <= slot <= 4:
            radiant.append(hero_id)
        elif 128 <= slot <= 132:
            dire.append(hero_id)
        else:
            return None
    if len(radiant) != 5 or len(dire) != 5:
        return None
    return radiant, dire


def record_heroes(heroes, radiant, dire, radiant_win, duration):
    """Accumulate per-hero pick/win/duration stats for one included match."""
    for hero_id in radiant:
        stats = heroes.setdefault(str(hero_id), new_hero_stats())
        stats["picks"] += 1
        stats["radiant_picks"] += 1
        stats["duration_sum"] += duration
        stats["duration_count"] += 1
        if radiant_win:
            stats["wins"] += 1
            stats["radiant_wins"] += 1
    for hero_id in dire:
        stats = heroes.setdefault(str(hero_id), new_hero_stats())
        stats["picks"] += 1
        stats["dire_picks"] += 1
        stats["duration_sum"] += duration
        stats["duration_count"] += 1
        if not radiant_win:
            stats["wins"] += 1
            stats["dire_wins"] += 1


def record_pairs(pair_synergy, pair_counter, radiant, dire, radiant_win):
    """Accumulate same-team synergy and opposite-team counter stats for one included match."""
    for team, won in ((radiant, radiant_win), (dire, not radiant_win)):
        for i, hero_a in enumerate(team):
            for hero_b in team[i + 1 :]:
                key = f"{min(hero_a, hero_b)}:{max(hero_a, hero_b)}"
                entry = pair_synergy.setdefault(key, {"count": 0, "wins": 0})
                entry["count"] += 1
                if won:
                    entry["wins"] += 1
    # Store both directions so each key "a:b" is a self-contained "a vs b" stat.
    for radiant_hero in radiant:
        for dire_hero in dire:
            key = f"{radiant_hero}:{dire_hero}"
            entry = pair_counter.setdefault(key, {"count": 0, "a_wins": 0})
            entry["count"] += 1
            if radiant_win:
                entry["a_wins"] += 1
            key = f"{dire_hero}:{radiant_hero}"
            entry = pair_counter.setdefault(key, {"count": 0, "a_wins": 0})
            entry["count"] += 1
            if not radiant_win:
                entry["a_wins"] += 1


def record_first_picks(first_pick, picks_bans, radiant_win):
    """Accumulate, per hero, how often each team first-picked it and whether that team won."""
    if not picks_bans:
        return
    for team in (0, 1):
        picks = [pb for pb in picks_bans if pb.get("is_pick") and pb.get("team") == team]
        if not picks:
            continue
        first_hero = min(picks, key=lambda pb: pb["order"])["hero_id"]
        won = radiant_win if team == 0 else not radiant_win
        entry = first_pick.setdefault(str(first_hero), {"count": 0, "wins": 0})
        entry["count"] += 1
        if won:
            entry["wins"] += 1


def load_hero_names():
    """Map hero id -> display name from the app roster, for the console summary."""
    with open(HEROES_JSON_PATH) as fp:
        return {str(hero["id"]): hero["name"] for hero in json.load(fp)}


def print_summary(meta, heroes):
    excluded = meta["excluded_by_reason"]
    print(f"\nTotal entries processed: {meta['total']}")
    print(f"Included: {meta['included']}")
    reasons = ", ".join(f"{reason}: {excluded[reason]}" for reason in EXCLUSION_REASONS)
    print(f"Excluded: {meta['excluded']} ({reasons})")
    included = meta["included"]
    ratio = 100 * meta["radiant_wins"] / included if included else 0.0
    print(f"Radiant win ratio: {ratio:.1f}% ({meta['radiant_wins']}/{included})")
    modes = ", ".join(f"{mode}: {count}" for mode, count in sorted(meta["game_modes"].items()))
    print(f"Game modes: {modes}")
    top = sorted(heroes.items(), key=lambda kv: kv[1]["picks"], reverse=True)[:3]
    names = load_hero_names()
    ranking = ", ".join(
        f"{names.get(hero_id, hero_id)} ({stats['picks']})" for hero_id, stats in top
    )
    print(f"Top 3 heroes by picks: {ranking}")
    print(f"League matches: {meta['league_matches']}")


def main():
    args = parse_args()
    if not ZIP_PATH.exists():
        raise SystemExit(f"Archive not found: {ZIP_PATH} (download it first, see docs/TODO.md)")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    heroes = {}
    pair_synergy = {}
    pair_counter = {}
    first_pick = {}
    excluded = {reason: 0 for reason in EXCLUSION_REASONS}
    game_modes = {}
    total = included = radiant_wins = league_matches = 0

    with zipfile.ZipFile(ZIP_PATH) as archive, open(CSV_PATH, "w") as csv_file:
        names = archive.namelist()
        if args.limit:
            names = names[: args.limit]
        csv_file.write(CSV_HEADER + "\n")

        for name in tqdm(names, desc="Streaming matches", unit="match"):
            file_match_id = name.rsplit("/", 1)[-1].removesuffix(".json")
            with archive.open(name) as fp:
                result = json.load(fp)["result"]
            total += 1
            players = result.get("players", [])

            if any(player.get("leaver_status", 0) >= 2 for player in players):
                excluded["leaver"] += 1
            elif result.get("human_players") != 10:
                excluded["human_players"] += 1
            elif (teams := split_teams(players)) is None:
                excluded["invalid_heroes"] += 1
            elif str(result.get("match_id")) != file_match_id:
                excluded["match_id_mismatch"] += 1
            else:
                radiant, dire = teams
                included += 1
                radiant_win = result["radiant_win"]
                if radiant_win:
                    radiant_wins += 1
                if result.get("leagueid", 0):
                    league_matches += 1
                mode = result["game_mode"]
                game_modes[mode] = game_modes.get(mode, 0) + 1

                record_heroes(heroes, radiant, dire, radiant_win, result["duration"])
                record_pairs(pair_synergy, pair_counter, radiant, dire, radiant_win)
                record_first_picks(first_pick, result.get("picks_bans"), radiant_win)
                csv_file.write(",".join(map(str, radiant + dire)) + f",{int(radiant_win)}\n")

    meta = {
        "total": total,
        "included": included,
        "excluded": sum(excluded.values()),
        "excluded_by_reason": dict(excluded),
        "radiant_wins": radiant_wins,
        "game_modes": game_modes,
        "league_matches": league_matches,
        "limit": args.limit,
    }
    hero_stats = {
        "meta": meta,
        "heroes": heroes,
        "pair_synergy": pair_synergy,
        "pair_counter": pair_counter,
        "first_pick": first_pick,
    }
    HERO_STATS_PATH.write_text(json.dumps(hero_stats, indent=2) + "\n")
    EXCLUSION_REPORT_PATH.write_text(json.dumps(meta, indent=2) + "\n")

    print(f"[OK] {HERO_STATS_PATH}")
    print(f"[OK] {CSV_PATH}")
    print(f"[OK] {EXCLUSION_REPORT_PATH}")
    print_summary(meta, heroes)


if __name__ == "__main__":
    main()
