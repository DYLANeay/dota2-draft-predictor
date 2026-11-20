"""Tests for POST /api/ask. The LLM is stubbed; nothing here touches the network."""

import asyncio

import pytest
from llm_interaction import AgentResult, LLMInteraction

import doracle.app as app_module
from doracle.app import app


@pytest.fixture()
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture()
def stub(monkeypatch):
    """Replace LLMInteraction with a stub and return its record of calls."""
    record = {"result": AgentResult(tool_call_count=1, stop_reason="content",
                                    final_content="ban Lina", response_id="r1")}

    class StubLLM:
        model = "stub-model"

        def __init__(self, **kwargs):
            record["init"] = kwargs

        async def agent_loop_template(self, prompt_name, variables, **kwargs):
            record["prompt_name"] = prompt_name
            record["variables"] = variables
            record["agent_loop"] = kwargs
            on_tool_call = kwargs.get("on_tool_call")
            if on_tool_call and not record.get("no_tool_calls"):
                on_tool_call(0, "resolve_hero", {"name": "Lina"}, {"id": 25, "name": "Lina"})
                on_tool_call(1, "submit_answer", {"answer": "the answer"}, "the answer")
            return record["result"]

    monkeypatch.setattr(app_module, "LLMInteraction", StubLLM)
    return record


def ask(client, **payload):
    return client.post("/api/ask", json=payload)


def test_question_reaches_the_prompt(client, stub):
    response = ask(client, question="Should we ban Lina?")

    assert response.status_code == 200
    assert stub["prompt_name"] == "chat"
    assert stub["variables"] == {"question": "Should we ban Lina?"}


def test_agent_loop_gets_tools_and_budget(client, stub):
    ask(client, question="hi")

    agent_loop = stub["agent_loop"]
    assert [tool.name for tool in agent_loop["tools"]] == [
        "resolve_hero",
        "list_heroes",
        "hero_stats",
        "submit_answer",
    ]
    assert agent_loop["max_tool_calls"] == 20


def test_prompt_files_match_the_template_name():
    """agent_loop_template renders {prompt_name}_system.jinja and _user.jinja.

    The client is built with a dummy key, so nothing here hits the network.
    """
    llm = LLMInteraction(
        prompt_dir=app_module.prompts_directory,
        backend="deepseek",
        api_key="dummy-key",
        model="deepseek-chat",
    )

    assert llm.render("chat_user.jinja", {"question": "ban Lina?"}).strip() == "ban Lina?"
    assert "Dota Oracle" in llm.render("chat_system.jinja", {})


def test_one_client_per_request(client, stub):
    ask(client, question="first")
    first_init = stub["init"]
    ask(client, question="second")

    assert first_init is not stub["init"]
    assert first_init["backend"] == "deepseek"
    assert first_init["max_retries"] == 1


def test_answer_comes_from_submit_answer(client, stub):
    stub["result"] = AgentResult(tool_call_count=2, stop_reason="stop_tool",
                                 final_content=None, response_id="r2")

    body = ask(client, question="hi").get_json()

    assert body["answer"] == "the answer"
    assert body["stop_reason"] == "stop_tool"
    assert [call["name"] for call in body["tool_calls"]] == ["resolve_hero", "submit_answer"]


def test_answer_comes_from_final_content(client, stub):
    stub["result"] = AgentResult(tool_call_count=0, stop_reason="content",
                                 final_content="play safe", response_id="r3")

    body = ask(client, question="hi").get_json()

    assert body["answer"] == "play safe"


def test_running_out_of_tool_budget_is_a_504(client, stub):
    stub["result"] = AgentResult(tool_call_count=20, stop_reason="max_calls",
                                 final_content=None, response_id="r4")

    response = ask(client, question="hi")

    assert response.status_code == 504
    assert "tool budget" in response.get_json()["error"]


def test_timeout_is_a_504(client, stub, monkeypatch):
    monkeypatch.setattr(app_module, "llm_timeout_s", 0.01)

    class SlowLLM:
        model = "stub-model"

        def __init__(self, **kwargs):
            pass

        async def agent_loop_template(self, *args, **kwargs):
            await asyncio.sleep(5)
            raise AssertionError("should have timed out")

    monkeypatch.setattr(app_module, "LLMInteraction", SlowLLM)

    assert ask(client, question="hi").status_code == 504


def test_provider_error_is_a_502(client, stub, monkeypatch):
    class BrokenLLM:
        model = "stub-model"

        def __init__(self, **kwargs):
            pass

        async def agent_loop_template(self, *args, **kwargs):
            raise RuntimeError("provider exploded")

    monkeypatch.setattr(app_module, "LLMInteraction", BrokenLLM)

    response = ask(client, question="hi")

    assert response.status_code == 502
    assert "provider exploded" in response.get_json()["error"]


def test_missing_configuration_is_a_503(client, monkeypatch):
    class UnconfiguredLLM:
        def __init__(self, **kwargs):
            raise ValueError("Model required. Set LLM_INTERACTION_MODEL or pass model=.")

    monkeypatch.setattr(app_module, "LLMInteraction", UnconfiguredLLM)

    response = ask(client, question="hi")

    assert response.status_code == 503
    assert "not configured" in response.get_json()["error"]


@pytest.mark.parametrize("question", ["", "   ", None])
def test_empty_question_is_a_400(client, stub, question):
    assert ask(client, question=question).status_code == 400


def test_long_question_is_a_400(client, stub):
    assert ask(client, question="x" * 2001).status_code == 400


def test_draft_is_echoed_back(client, stub):
    body = ask(
        client,
        question="hi",
        radiant=[1, 5],
        dire=[2],
        radiant_bans=[25],
        dire_bans=[11, 52],
    ).get_json()

    assert body["draft_echo"] == {
        "radiant": [1, 5],
        "dire": [2],
        "radiant_bans": [25],
        "dire_bans": [11, 52],
    }


def test_missing_draft_lists_become_empty(client, stub):
    body = ask(client, question="hi").get_json()

    assert body["draft_echo"] == {
        "radiant": [],
        "dire": [],
        "radiant_bans": [],
        "dire_bans": [],
    }


def test_unknown_payload_keys_are_ignored(client, stub):
    response = ask(client, question="hi", history=[{"role": "user", "content": "old"}])

    assert response.status_code == 200
    assert "history" not in stub["agent_loop"]
