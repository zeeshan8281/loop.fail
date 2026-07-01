"""CI guard: every leaderboard row must be well-formed and its score must match the
formula recomputed from (cost, iterations, squad_size). Catches the cheapest cheat —
fudging the score arithmetic — without needing any API keys.

  python verify_leaderboard.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from architectures import ARCHITECTURES
from scorer import score

ROOT = Path(__file__).parent
REQUIRED = {"task", "solver", "architecture", "squad_size", "solved",
            "cost", "iterations", "score", "run_hash", "created"}
TASKS = {p.name for p in (ROOT / "tasks").glob("[0-9]*") if p.is_dir()}


def check(rows) -> list[str]:
    errs = []
    for i, r in enumerate(rows):
        where = f"row {i} (@{r.get('solver','?')}/{r.get('task','?')})"
        missing = REQUIRED - set(r)
        if missing:
            errs.append(f"{where}: missing fields {sorted(missing)}")
            continue
        if r["task"] not in TASKS:
            errs.append(f"{where}: unknown task {r['task']!r} (have {sorted(TASKS)})")
        if r["architecture"] not in ARCHITECTURES:
            errs.append(f"{where}: bad architecture {r['architecture']!r}")
        if r["squad_size"] not in (3, 5, 7):
            errs.append(f"{where}: squad_size must be 3/5/7, got {r['squad_size']}")
        if not r["solved"]:
            errs.append(f"{where}: unsolved runs don't belong on the board")
        expect = score(r["cost"], r["iterations"], r["squad_size"])
        if r["score"] != expect:
            errs.append(f"{where}: score {r['score']} != formula {expect} "
                        f"(cost {r['cost']}, iters {r['iterations']}, squad {r['squad_size']})")
    return errs


def main() -> int:
    rows = yaml.safe_load((ROOT / "leaderboard.yaml").read_text()) or []
    errs = check(rows)
    if errs:
        print("leaderboard.yaml FAILED:")
        for e in errs:
            print("  -", e)
        return 1
    print(f"leaderboard.yaml ok — {len(rows)} rows, all scores match the formula")
    return 0


if __name__ == "__main__":
    sys.exit(main())
