# Loop Squad

> Design the smallest, cheapest team of agents that solves the task. **Lowest score wins.**
> Sibling to Prompt Golf, for the Eigen Builder Collective — Session 5 (Loop Engineering).

Prompt Golf optimizes a single prompt. Loop Squad optimizes a *system*: a squad of
3 / 5 / 7 agents plus an architecture, run in a bounded loop against a sealed task.

**[→ Live leaderboard](https://eigen-labs.github.io/loop-squad/)**

## Play in 60 seconds — the `loop` CLI

New here? Load the [get-started skill](skills/loop-squad/SKILL.md) into your agent, or just:

```bash
git clone <your fork> && cd loop-squad
pip install -r requirements.txt
./loop config --handle <your_github_handle>
export DARKBLOOM_API_KEY=...          # and/or ANTHROPIC_API_KEY / OPENAI_API_KEY

./loop tasks                          # see the three problems
./loop start 001 --handle <you>       # scaffold submissions/<you>.py from a starter loop
#   ...edit the squad: prompts, models, size (3/5/7)...
./loop run 001                        # run it (add --mock for a keyless dry run)
./loop submit 001                     # append your result + get the PR commands
```

`run` prints a result block; `submit` only accepts a solved, non-mock run and writes your
row to `leaderboard.yaml`. CI checks it; merge puts you on the board.

```
── result ────────────────────────────
task:         001_fix_bugs
solver:       @aashatwt
architecture: 3-agent supervisor
solved:       yes
cost:         $0.0110
iterations:   3
wallclock:    41s
score:        32
run_hash:     8a2fcd…9b3e
───────────────────────────────────────
```

<details><summary>Prefer raw scripts over the CLI?</summary>

```bash
cp starters/supervisor_3.py submissions/<you>.py
python runner.py --task 001 --submission submissions/<you>.py
```
</details>

## Scoring

```
score = round(cost_usd * 1000 + iterations * 5 + squad_size * 2)   # lower wins
```

- **Cost dominates** — the cheapest *correct* solution wins.
- **Iteration penalty** rewards tight prompts and good supervisors.
- **Squad-size penalty** kills the "throw 7 agents at it" reflex (a 3-agent squad starts 8 points ahead of a 7-agent one).

You only score if your squad produces the correct output on the sealed tests.

## The submission

A single file `submissions/<handle>.py` exporting a `SQUAD` dict:

```python
SQUAD = {
    "architecture": "supervisor",   # sequential | debate | supervisor | manager
    "agents": [                      # exactly 3, 5, or 7
        {"role": "planner",   "prompt": "...", "model": "claude-haiku-4-5",
         "base_url": "https://api.anthropic.com/v1", "pricing": {"in": 1.0, "out": 5.0}},
        {"role": "executor",  "prompt": "...", "model": "qwen3.5-27b",
         "base_url": "https://api.darkbloom.dev/v1", "pricing": {"in": 0.10, "out": 0.78},
         "api_key_env": "DARKBLOOM_API_KEY"},
        {"role": "supervisor","prompt": "...", "model": "claude-haiku-4-5",
         "base_url": "https://api.anthropic.com/v1", "pricing": {"in": 1.0, "out": 5.0}},
    ],
}
```

- `pricing` is in **$ per 1,000,000 tokens**.
- Any OpenAI-compatible endpoint is allowed. `api_key_env` names the env var holding that endpoint's key (defaults to `OPENAI_API_KEY`, then `LLM_API_KEY`).
- Your squad emits output files in this exact form:
  ```
  <<<FILE path=stats.py>>>
  ...file content...
  <<<END>>>
  ```

## The four architectures

| Name | Abbr | What it does |
| --- | --- | --- |
| `sequential` | seq | Agents run in order; each gets the previous output. Simplest. |
| `debate` | deb | All answer, see each other, revise; a moderator picks the final. |
| `supervisor` | sup | The Session 5 pattern — a supervisor verifies the workers; unverified → retry. |
| `manager` | mgr | A planner assigns subtasks, collects, and synthesizes. |

You can't define your own — pick one. The **kill switch** is built in: every loop is bounded by the task's `meta.yaml` caps (iterations, tokens, wallclock).

## Tasks — pick your problem

Three problems, ramping up (`./loop tasks`). Each lives in `tasks/NNN_*/`
(`task.md` · `inputs/` · sealed tests · caps); the menu is `tasks.yaml`.

| ID | Name | What your squad solves | Difficulty |
| --- | --- | --- | --- |
| 001 | `fix_bugs` | Fix three bugs in a run-length codec so `encode`/`decode` round-trip. | warmup |
| 002 | `implement` | Implement `calc(expr)` — an integer expression evaluator with precedence + parens. | medium |
| 003 | `extract` | Parse a messy invoice into structured JSON; compute the total yourself. | medium |

## Starter loops

`./loop start` scaffolds from these; you can also copy them by hand:

| File | Loop | Best for |
| --- | --- | --- |
| `starters/sequential_3.py` | 3-agent sequential, all Darkbloom | 002 |
| `starters/supervisor_3.py` | 3-agent supervisor (the Session 5 pattern) | 001 |
| `starters/debate_5.py` | 5-agent debate + moderator | 003 |

## Repo map

```
loop / loop_cli.py   the CLI — config · tasks · start · run · submit · submissions
skills/loop-squad/   the get-started skill — the agent's full playbook
runner.py            the bounded loop + hashing      (DO NOT EDIT)
scorer.py            the scoring formula             (DO NOT EDIT)
verifier.py          runs the sealed tests           (DO NOT EDIT)
architectures/       the four presets
tasks/NNN_*/         task.md · inputs/ · tests.sealed · meta.yaml
tasks.yaml           the problem menu (drives the CLI + leaderboard tabs)
starters/            copyable reference squads (loops) per architecture
submissions/         template.py + one file per builder
leaderboard.yaml     PR target — one row per (task, solver)
docs/                GitHub Pages leaderboard (Eigen design system)
verify_leaderboard.py  CI guard: row shape + score arithmetic
tests/test_smoke.py  offline end-to-end check (no API keys)
```

## Trust

Invite-only Collective, not Kaggle — kept light (PRD §11):
deterministic `run_hash` · CI re-run when the model is reachable (else a *self-reported* badge) ·
public submission files anyone can re-run · quarterly top-3 spot-checks · honor system for the rest.

## Dev

```bash
python -m pytest tests/ -q     # end-to-end, offline
python scorer.py               # formula self-check
python verify_leaderboard.py   # validate the board
python runner.py --task 001 --submission submissions/aashatwt.py --mock   # dry-run, no keys
```
