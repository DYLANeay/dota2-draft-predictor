"""Regression tests for hero id lookups.

`heroes.json` is a list whose indices do not match hero ids, so `/stats/<id>`
must resolve heroes by id, not by list position.
"""

import pytest

from doracle.app import app, get_heroes, get_heroes_by_id


@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client


def test_roster_index_is_not_id():
    """Guard the premise of the bug this module pins down."""
    heroes = get_heroes()
    mismatched = [h for i, h in enumerate(heroes) if h["id"] != i]
    assert mismatched, "heroes.json unexpectedly ordered by id; revisit these tests"
    assert len({h["id"] for h in heroes}) == len(heroes), "duplicate hero ids"


@pytest.mark.parametrize(
    ("hero_id", "expected_name"),
    [
        (52, "Leshrac"),  # list index 52 holds "Life Stealer"
        (106, "Ember Spirit"),  # list index 106 holds "Phoenix"
        (135, "Dawnbreaker"),
        (1, "Antimage"),
    ],
)
def test_stats_resolves_hero_by_id(client, hero_id, expected_name):
    response = client.get(f"/stats/{hero_id}")
    assert response.status_code == 200
    assert response.get_json()["hero"] == expected_name


@pytest.mark.parametrize("hero_id", [24, 115, 122, 127, 999, 0])
def test_unknown_hero_id_returns_404(client, hero_id):
    response = client.get(f"/stats/{hero_id}")
    assert response.status_code == 404
    assert response.get_json()["heroid"] == hero_id


def test_best_paired_with_is_a_real_hero_or_none(client):
    """The stub model can emit ids that are not in the roster; never crash."""
    valid_names = {hero["name"] for hero in get_heroes()}
    for _ in range(50):
        partner = client.get("/stats/1").get_json()["best_paired_with"]
        assert partner is None or partner in valid_names


def test_heroes_by_id_is_keyed_by_id():
    by_id = get_heroes_by_id()
    assert len(by_id) == len(get_heroes())
    assert all(hero_id == hero["id"] for hero_id, hero in by_id.items())
