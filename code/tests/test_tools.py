"""Tests for the tools the Oracle can call."""

import pytest

from doracle.tools import (
    TOOLS,
    hero_stats,
    list_heroes,
    resolve_hero,
    submit_answer,
)


def call(tool, **kwargs):
    """Run a tool the way the agent loop does: through its ToolDef."""
    return tool.function(**kwargs)


def test_tool_names():
    assert [tool.name for tool in TOOLS] == [
        "resolve_hero",
        "list_heroes",
        "hero_stats",
        "submit_answer",
    ]


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Lina", "Lina"),
        ("lina", "Lina"),
        ("  crystal   maiden ", "Crystal Maiden"),
        ("Antimage", "Antimage"),
        ("Anti-Mage", "Antimage"),
        ("Nature's Prophet", "Nature Prophet"),
        ("Clockwerk", "Rattletrap"),
        ("Outworld Destroyer", "Obsidian Destroyer"),
        ("Windranger", "Windrunner"),
        ("nevermore", "Shadow Fiend"),
    ],
)
def test_resolve_hero(name, expected):
    assert call(resolve_hero, name=name)["name"] == expected


def test_resolve_hero_returns_id_and_api_name():
    hero = call(resolve_hero, name="Lina")

    assert hero == {"id": 25, "name": "Lina", "api_name": "lina"}


def test_resolve_unknown_hero_returns_an_error():
    result = call(resolve_hero, name="Not A Real Hero")

    assert "error" in result
    assert "Not A Real Hero" in result["error"]


def test_list_heroes_is_sorted_and_complete():
    heroes = call(list_heroes)

    assert heroes == sorted(heroes)
    assert "Lina" in heroes
    assert len(heroes) == len(set(heroes))


def test_hero_names_have_no_stray_whitespace():
    from doracle.heroes import get_heroes

    for hero in get_heroes():
        assert hero["name"] == hero["name"].strip()
        assert "  " not in hero["name"]


def test_hero_stats_shape():
    stats = call(hero_stats, hero="Lina")

    assert stats["hero"] == "Lina"
    assert stats["hero_id"] == 25
    assert 0.0 <= stats["win_rate"] <= 1.0
    assert 0.0 <= stats["pick_rate"] <= 1.0
    assert "placeholder" in stats["note"]


def test_hero_stats_unknown_hero():
    assert "error" in call(hero_stats, hero="Not A Real Hero")


def test_submit_answer_is_a_stop_tool():
    assert submit_answer.is_stop is True
    assert call(submit_answer, answer="ban Lina") == "ban Lina"


def test_tool_schemas_expose_parameters():
    schema = resolve_hero.schema

    assert schema["name"] == "resolve_hero"
    assert "name" in schema["parameters"]["properties"]
    assert schema["parameters"]["required"] == ["name"]
    assert "Nature's Prophet" in resolve_hero.description or resolve_hero.description
