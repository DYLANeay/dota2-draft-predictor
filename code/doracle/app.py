# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import asyncio
import getpass
import os
from functools import lru_cache

import requests as req
from dotenv import load_dotenv
from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from llm_interaction import LLMInteraction

from doracle.heroes import get_heroes, get_heroes_by_id

# The ML model files
from doracle.model import HeroStats
from doracle.predictor import WEIGHTS_PATH, WinPredictor
from doracle.tools import TOOLS

package_directory = os.path.dirname(os.path.abspath(__file__))
project_directory = os.path.dirname(package_directory)
prompts_directory = os.path.join(package_directory, "prompts")

# Loaded from an explicit path so the .env is found even when the app is started
# from another directory.
load_dotenv(os.path.join(project_directory, ".env"))

# ----------------------------------------------------------------------------#
# Configs
# ----------------------------------------------------------------------------#

frontend_port = 5000
app = Flask(__name__, static_folder='static', template_folder='templates')

# TODO: Remove before prod
running_user = getpass.getuser()

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
debug_mode = True

# How many tools the Oracle may call while answering one question.
# Raise this if you give it more tools to work with.
max_tool_calls = 20

# Seconds to wait for the Oracle before giving up.
llm_timeout_s = float(os.getenv("LLM_TIMEOUT_S", "60"))

# ----------------------------------------------------------------------------#
# Renders
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("index.html", heroes=get_heroes())


@app.route("/explore")
def explore():
    return render_template("explore.html", heroes=get_heroes())


# ----------------------------------------------------------------------------#
# Oracle
# ----------------------------------------------------------------------------#

@app.route("/api/ask", methods=["POST"])
def ask():
    payload = request.get_json(silent=True) or {}

    question = str(payload.get("question") or "").strip()
    if not question:
        return jsonify({"error": "question is required"}), 400
    if len(question) > 2000:
        return jsonify({"error": "question must be at most 2000 characters"}), 400

    draft_echo = {
        key: payload.get(key, [])
        for key in ("radiant", "dire", "radiant_bans", "dire_bans")
    }

    try:
        # One client per request: it is used once and thrown away, so there is
        # no shared state to go stale between questions.
        llm = LLMInteraction(
            prompt_dir=prompts_directory, backend="deepseek", max_retries=1
        )
    except ValueError as exc:
        return jsonify({"error": f"LLM backend not configured: {exc}"}), 503

    tool_calls = []

    def on_tool_call(index, name, args, result):
        print("[tool]", name)
        tool_calls.append({"name": name, "args": args, "result": result})

    try:
        result = asyncio.run(
            asyncio.wait_for(
                # Renders prompts/chat_system.jinja and prompts/chat_user.jinja,
                # then runs the tool-calling loop.
                llm.agent_loop_template(
                    prompt_name="chat",
                    variables={"question": question},
                    tools=TOOLS,
                    max_tool_calls=max_tool_calls,
                    on_tool_call=on_tool_call,
                ),
                timeout=llm_timeout_s,
            )
        )
    except TimeoutError:
        return jsonify({"error": "the Oracle timed out", "tool_calls": tool_calls}), 504
    except Exception as exc:
        return jsonify({"error": str(exc), "tool_calls": tool_calls}), 502

    if result.stop_reason == "stop_tool":
        answer = next(
            (
                call["result"]
                for call in reversed(tool_calls)
                if call["name"] == "submit_answer"
            ),
            "",
        )
    elif result.stop_reason == "content":
        answer = result.final_content or ""
    else:
        return (
            jsonify({"error": "the Oracle ran out of tool budget", "tool_calls": tool_calls}),
            504,
        )

    print(f"answered in {result.tool_call_count} tool call(s)")

    return jsonify(
        {
            "answer": answer,
            "model": llm.model,
            "stop_reason": result.stop_reason,
            "tool_calls": tool_calls,
            "draft_echo": draft_echo,
        }
    )


# <button 1>
@app.route("/suggest1", methods=["POST"])
def suggest1():
    r = request.get_json(silent=True) or {}

    # Probability that Radiant wins the given (possibly partial) draft.
    p = get_win_predictor().predict(r.get("radiant", []), r.get("dire", []))

    return jsonify(
        {
            "radiant": r.get("radiant", []),
            "dire": r.get("dire", []),
            "radiant_win_probability": round(p, 3),
            "dire_win_probability": round(1 - p, 3),
            "predicted_winner": "radiant" if p >= 0.5 else "dire",
        }
    )

# <button 2>
@app.route("/suggest2", methods=["POST"])
def suggest2():
    r = request.get_json()
    r["todo"] = "Implement 'Dangerous Counter Picks' here."

    return jsonify(r)


# <button 3>
@app.route("/suggest3", methods=["POST"])
def suggest3():
    r = request.get_json()
    r["todo"] = "Implement 'Something Something Else' here."

    return jsonify(r)

# ----------------------------------------------------------------------------#
# Explore
# ----------------------------------------------------------------------------#


@app.route("/stats/<int:heroid>", methods=["GET"])
def get_hero_stats(heroid):
    heroes_by_id = get_heroes_by_id()

    hero = heroes_by_id.get(heroid)
    if hero is None:
        return jsonify({"error": "unknown hero id", "heroid": heroid}), 404

    hero_model = get_hero_stat_model()
    win_rate = hero_model.get_winrate(heroid)
    pick_rate = hero_model.get_pickrate(heroid)
    best_paired_with = hero_model.get_best_paired_with_hero(heroid)

    partner = heroes_by_id.get(best_paired_with)

    hero_stats = {
        "todo": "please implement this feature instead of the random stats that are not used.",
        "hero": hero["name"],
        "win_rate": win_rate,
        "pick_rate": pick_rate,
        "best_paired_with": partner["name"] if partner else None,
    }

    print("hero_stats:", hero_stats)

    return jsonify(hero_stats)

# ----------------------------------------------------------------------------#
# Helpers
# ----------------------------------------------------------------------------#
@lru_cache(maxsize=1)
def get_hero_stat_model():
    path_to_model = "/home/dota_oracle_user/models/herostat.pkl"

    hero_stat_model = HeroStats.load(path_to_model)
    return hero_stat_model


# Le modèle de prédiction, chargé une seule fois depuis les poids entraînés
@lru_cache(maxsize=1)
def get_win_predictor():
    return WinPredictor.load(WEIGHTS_PATH)


def main():
    app.jinja_env.cache = {}
    app.run(debug=debug_mode, host='127.0.0.1', port=frontend_port)


if __name__ == '__main__':
    main()
