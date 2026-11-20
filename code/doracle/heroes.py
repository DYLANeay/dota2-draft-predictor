"""Hero roster: loading, name normalisation and lookup."""

import json
import os
import re
from functools import lru_cache

package_directory = os.path.dirname(os.path.abspath(__file__))
HEROES_PATH = os.path.join(package_directory, "data", "heroes.json")

# Names players use that do not match the (old) names in heroes.json.
# Values are the api_name of the hero they point at.
_ALIAS_NAMES = {
    "clockwerk": "rattletrap",
    "outworld destroyer": "obsidian_destroyer",
    "windranger": "windrunner",
    "nature's prophet": "furion",
    "treant protector": "treant",
    "centaur warrunner": "centaur",
}


def _name_key(name: str) -> str:
    """Reduce a hero name to a comparable key ("Anti-Mage" -> "antimage")."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


ALIASES = {_name_key(alias): api_name for alias, api_name in _ALIAS_NAMES.items()}


@lru_cache(maxsize=1)
def get_heroes() -> list[dict]:
    """Hero records, in the order stored in heroes.json."""
    with open(HEROES_PATH) as fp:
        heroes = json.load(fp)

    # heroes.json was generated from the Steam Web API, which pads some names.
    for hero in heroes:
        hero["name"] = " ".join(hero["name"].split())

    return heroes


@lru_cache(maxsize=1)
def get_heroes_by_id() -> dict[int, dict]:
    """Hero id -> hero record.

    heroes.json is a list in arbitrary order and its indices do NOT match hero
    ids: the ids are sparse (24, 115-118, 122-125, 127, ... are unused) and some
    entries are out of order, so the list must never be indexed by hero id.
    """
    return {hero["id"]: hero for hero in get_heroes()}


@lru_cache(maxsize=1)
def get_heroes_by_name() -> dict[str, dict]:
    """Lookup key -> hero record, matching both display and api names."""
    by_name = {}
    for hero in get_heroes():
        by_name[_name_key(hero["name"])] = hero
        by_name[_name_key(hero["api_name"])] = hero
    return by_name


def find_hero(name: str) -> dict | None:
    """Find a hero by name, tolerating casing, spacing and older names."""
    by_name = get_heroes_by_name()

    hero = by_name.get(_name_key(name))
    if hero is not None:
        return hero

    alias = ALIASES.get(_name_key(name))
    if alias is not None:
        return by_name.get(_name_key(alias))

    return None
