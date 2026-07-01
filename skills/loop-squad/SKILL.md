---
name: loop-squad
description: "Get started with Loop Squad using the `loop` CLI: config, tasks, task, start, run, submit, submissions, version, install-skill. Design a 3/5/7-agent squad + architecture, run it locally against a sealed task with your own API keys, and open a leaderboard PR. Use when a solver or coding agent wants to enter Loop Squad, pick a problem, build/tune a squad, run a task, improve a score, or submit a benchmark result."
---

# Loop Squad — get started

Loop Squad is a game for the Eigen Builder Collective (Session 5, Loop Engineering).
You field the **smallest, cheapest squad of agents that solves the task**. Score, lower wins:

```
score = cost_usd*1000 + iterations*5 + squad_size*2
```

You only score if the sealed tests pass. There's no server and no login — your **GitHub
handle is your identity** and **your own API keys** do the work. Everything runs locally
through the `loop` CLI from inside the repo.

## Setup

Clone/fork the repo, install deps, and set your handle + a provider key:

```bash
git clone https://github.com/eigen-labs/loop-squad && cd loop-squad
pip install -r requirements.txt
./loop config --handle <your_github_handle>
export DARKBLOOM_API_KEY=...      # and/or ANTHROPIC_API_KEY / OPENAI_API_KEY
```

`./loop config` shows your handle, which provider keys are visible in the env, and the repo
path. Run all `loop` commands from the repo root (or symlink `./loop` onto your PATH).

Each agent in a squad names the env var holding its endpoint's key via `api_key_env`
(default `OPENAI_API_KEY`, then `LLM_API_KEY`). Export whatever your squad uses.

## Pick a problem

```bash
./loop tasks            # the three problems, with difficulty + blurb
./loop task 001         # read one problem's full brief
```

Three problems ship: `001 fix_bugs` (warmup), `002 implement` (medium), `003 extract` (medium).

## Build your squad (the loop)

Scaffold a submission from a starter loop — don't start from a blank file:

```bash
./loop start 001 --handle <you>     # copies a starter into submissions/<you>.py
```

`start` picks the starter suggested for that task; override with `--arch sequential|debate|supervisor|manager`.
Then edit `submissions/<you>.py`:

- **Squad size must be 3, 5, or 7.** Architecture is one of `sequential`, `debate`, `supervisor`, `manager` (you can't define your own).
- Each agent needs `role`, `prompt`, `model`, `base_url`, `pricing {in, out}` (in **$/1M tokens**), and optionally `api_key_env`.
- Your squad emits output files as `<<<FILE path=NAME>>> ... <<<END>>>` — the runner parses that.

Optimize for **score, not horsepower**: cost dominates, so keep cheap models (Darkbloom's
`qwen3.5-27b` is usually the cheapest correct option) on the heavy-lifting agents and a
stronger model only where reasoning is needed. Start at **3 agents**; only grow to 5/7 if 3
can't crack it. Tight prompts + a real supervisor cut iterations. The `starters/` files show
each pattern.

## Run it

```bash
./loop run 001                 # runs submissions/<you>.py against task 001
./loop run 001 --mock          # keyless dry run — exercises the loop, won't solve
```

The runner pins `temperature=0` and enforces the task's **kill-switch caps** (max iterations,
tokens, wallclock from `meta.yaml`). It prints a result block with `solved`, `cost`,
`iterations`, `score`, and a deterministic `run_hash`, and caches the run. If `solved: no`,
iterate: tighten prompts, swap in a cheaper model, drop an agent, or change architecture — then re-run.

## Submit

When the last run shows `solved: yes`, append it to the leaderboard and open a PR:

```bash
./loop submit 001              # appends your row to leaderboard.yaml (+ docs copy)
python verify_leaderboard.py   # sanity-check row shape + score arithmetic
```

`submit` prints the exact `git` + `gh pr create` commands. Only push/open the PR when the
user asks. CI re-checks the row and (when it can reach your model) the `run_hash`; otherwise
the row keeps a **self-reported** badge. Unsolved or `--mock` runs are refused.

## Track the board

```bash
./loop submissions             # your rows
./loop submissions --all       # everyone's, per task (🏆 marks each task leader)
./loop submissions --task 002  # filter to one task
```

Check the board periodically — leaders move as builders learn. Beating the current best is
the whole game.

## Maintenance

```bash
./loop version                 # CLI version
./loop install-skill           # copy this skill into ~/.claude/skills (restart your agent after)
```

## Rules you must enforce
- Squad size ∈ {3, 5, 7}; architecture ∈ {sequential, debate, supervisor, manager}.
- Never edit `runner.py`, `scorer.py`, `verifier.py`, or anyone else's submission/rows.
- Don't fake `run_hash`, `cost`, or `score` — CI re-derives the math and spot-checks re-run the model.
- Unsolved runs don't go on the board.
