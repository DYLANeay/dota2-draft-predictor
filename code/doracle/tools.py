"""Tools the Oracle can call while answering a question."""

from llm_interaction import tool

from doracle.heroes import find_hero, get_heroes


# TODO:
# Add more tools as needed -> predict games perhaps?

@tool
def resolve_hero(name: str) -> dict:
    """Resolve a hero name to the entry the application uses.

    Accepts the names players write, including older ones.

    Args:
        name: Hero name as written by the user, e.g. "Nature's Prophet".
    """
    hero = find_hero(name)
    if hero is None:
        return {"error": f"unknown hero: {name!r}. Call list_heroes to see the roster."}

    return {"id": hero["id"], "name": hero["name"], "api_name": hero["api_name"]}


@tool
def list_heroes() -> list[str]:
    """List every hero name in the roster."""
    return sorted(hero["name"] for hero in get_heroes())


@tool
def hero_stats(hero: str) -> dict:
    """Win rate, pick rate and most common partner for a hero.

    Args:
        hero: Hero name, e.g. "Crystal Maiden".
    """
    # Imported here so the tool module stays importable on its own.
    from doracle.app import get_hero_stat_model

    resolved = find_hero(hero)
    if resolved is None:
        return {"error": f"unknown hero: {hero!r}. Call list_heroes to see the roster."}

    model = get_hero_stat_model()
    hero_id = resolved["id"]
    partner = model.get_best_paired_with_hero(hero_id)

    return {
        "hero": resolved["name"],
        "hero_id": hero_id,
        "win_rate": model.get_winrate(hero_id),
        "pick_rate": model.get_pickrate(hero_id),
        "best_paired_with_id": partner,
        "note": "placeholder model: these numbers are random and not real statistics",
    }


@tool(stop=True)
def submit_answer(answer: str) -> str:
    """Submit the final reply to the user. Always call this when you are done.

    Args:
        answer: The complete answer, as plain text.
    """
    return answer


TOOLS = [resolve_hero, list_heroes, hero_stats, submit_answer]
