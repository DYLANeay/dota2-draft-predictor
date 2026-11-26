"""Tests for WinPredictor and POST /suggest1. Pure Python, no network."""

import json
import math

import pytest

from doracle.app import app
from doracle.predictor import WEIGHTS_PATH, WinPredictor

RADIANT = [61, 6, 108, 56, 4]
DIRE = [70, 69, 121, 94, 72]


@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(scope="module")
def model():
    return WinPredictor.load(WEIGHTS_PATH)


@pytest.fixture(scope="module")
def raw():
    with open(WEIGHTS_PATH) as fp:
        return json.load(fp)


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def test_empty_draft_returns_sigmoid_of_bias(model, raw):
    assert model.predict([], []) == pytest.approx(sigmoid(raw["bias"]))


def test_single_radiant_hero(model, raw):
    weights, bias = raw["weights"], raw["bias"]

    for hero_id in RADIANT:
        assert model.predict([hero_id], []) == pytest.approx(sigmoid(weights[hero_id] + bias))


def test_single_dire_hero(model, raw):
    weights, bias = raw["weights"], raw["bias"]

    for hero_id in DIRE:
        assert model.predict([], [hero_id]) == pytest.approx(sigmoid(bias - weights[hero_id]))


def test_full_draft_matches_hand_computation(model, raw):
    weights, bias = raw["weights"], raw["bias"]
    z = bias + sum(weights[h] for h in RADIANT) - sum(weights[h] for h in DIRE)

    p = model.predict(RADIANT, DIRE)

    assert p == pytest.approx(sigmoid(z))
    assert 0.0 <= p <= 1.0


def test_string_hero_ids_match_int_ids(model):
    radiant_str = [str(h) for h in RADIANT]
    dire_str = [str(h) for h in DIRE]

    assert model.predict(radiant_str, dire_str) == pytest.approx(model.predict(RADIANT, DIRE))


def test_suggest1_route(client, model):
    response = client.post("/suggest1", json={"radiant": RADIANT, "dire": DIRE})

    assert response.status_code == 200
    body = response.get_json()
    p = model.predict(RADIANT, DIRE)

    assert body["radiant_win_probability"] == round(p, 3)
    assert body["dire_win_probability"] == round(1 - p, 3)
    assert body["radiant_win_probability"] + body["dire_win_probability"] == pytest.approx(
        1.0, abs=0.01
    )
    expected = "radiant" if p >= 0.5 else "dire"
    assert body["predicted_winner"] == expected


def test_suggest1_route_empty_draft(client, model):
    response = client.post("/suggest1", json={})

    assert response.status_code == 200
    body = response.get_json()
    p = model.predict([], [])

    assert body["radiant_win_probability"] == round(p, 3)
    expected = "radiant" if p >= 0.5 else "dire"
    assert body["predicted_winner"] == expected
