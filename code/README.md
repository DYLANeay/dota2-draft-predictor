# Dota Oracle

A small Dota 2 draft assistant. Pick and ban heroes, ask a question, get an
answer produced by an LLM that can call tools.

## Getting Started

### Prerequisites

* [uv](https://docs.astral.sh/uv/) — it installs Python and the dependencies for
  you. Install it with:
  * macOS / Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  * Windows (PowerShell): `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
* An internet connection for the first install
* A DeepSeek API key (ask your instructor)

You do **not** need Python installed beforehand. uv downloads the version pinned
in `.python-version` (3.12) the first time you run it.

### Install

Unzip the project and open a terminal in the project root (the folder with
`pyproject.toml` in it), then:

1. **Install the dependencies**

   ```bash
   uv sync
   ```

   This creates `.venv/` and installs everything, including the dev tools. The
   zip you received contains no `.venv/`, so this step is required.

2. **Add your API key**

   Copy the template and fill in the key:

   ```bash
   cp .env.example .env            # macOS / Linux
   Copy-Item .env.example .env     # Windows PowerShell
   ```

   Then open `.env` and set:

   ```
   LLM_INTERACTION_API_KEY=<your key>
   ```

   `.env` is gitignored. Never put a real key in `.env.example`.

3. **Check it works**

   ```bash
   uv run pytest
   ```

   The test suite needs no API key and no network. If it passes, the install
   is good.

### Run

```bash
uv run dota-oracle
```

Open http://127.0.0.1:5000 — you should see hero portraits on the left and the
Ask box on the right.

Equivalent ways to start it:

* `uv run python -m doracle.app` — same thing
* `uv run flask --app doracle.app run --debug --port 5001` — use this to pick a
  different port or get auto-reload on file changes

Stop the server with `Ctrl+C`.

### Troubleshooting

| Symptom | Cause |
| --- | --- |
| `503` / "LLM backend not configured" | `.env` is missing, or `LLM_INTERACTION_API_KEY` is still empty. Fix it and **restart** the server — `.env` is only read at startup. |
| `504` / "ran out of tool budget" | The question needed more than 20 tool calls. Ask something narrower. |
| `504` / "the Oracle timed out" | The model did not answer within `LLM_TIMEOUT_S` (default 60s). Try again, or raise the value in `.env`. |
| `Address already in use` | Something else is on port 5000. Use the `flask ... --port 5001` form above. |
| `502` | The provider rejected the call — usually a wrong or exhausted key. |
| Hero images are broken | You are offline; the portraits are local but the page also loads Bootstrap from a CDN. |

## Asking the Oracle

Pick heroes for Radiant and Dire (click a hero, then the green Radiant or red
Dire half), shift-click a half to **ban** instead, and click a filled slot to
clear it. Radiant and Dire each get 5 picks and 7 bans.

Then type a question in the Ask box and press Send (or Ctrl/Cmd+Enter). One
question gets one answer — there is no follow-up, so each Send is independent.

Every question is sent along with the current picks and bans.

## How the answer is produced

`llm-interaction` (non-streaming) against DeepSeek. Configuration comes from
`.env`:

| Variable | Meaning |
| --- | --- |
| `LLM_INTERACTION_BACKEND` | `deepseek` |
| `LLM_INTERACTION_API_KEY` | DeepSeek API key |
| `LLM_INTERACTION_MODEL` | e.g. `deepseek-chat` |
| `LLM_TIMEOUT_S` | Seconds to wait for an answer (default 60) |

The Oracle answers by calling tools, defined in `doracle/tools.py`:

| Tool | What it does |
| --- | --- |
| `resolve_hero` | turns a hero name into the roster entry (tolerates old names) |
| `list_heroes` | every hero name in the roster |
| `hero_stats` | win rate, pick rate and best partner (placeholder model) |
| `submit_answer` | sends the final reply and ends the loop |

Add tools there and list them in `TOOLS`; raise `max_tool_calls` in
`doracle/app.py` if the Oracle needs to call more of them per question.

The prompts live in `doracle/prompts/chat_system.jinja` and
`doracle/prompts/chat_user.jinja`, rendered by `agent_loop_template` with
`prompt_name="chat"`.

## Development

* `uv run pytest` — the test suite (no network, no API key)
* `uv run ruff check --fix` and `uv run ruff format` — lint and format

## License

[MIT License](LICENSE)
