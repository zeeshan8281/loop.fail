"""loop — the Loop Squad CLI. The front door for playing.

  loop tasks                    # the three problems
  loop task 001                 # read one problem
  loop start 001 --handle you   # scaffold submissions/you.py from a starter loop
  loop run 001                  # run your squad locally (add --mock for a keyless dry run)
  loop submit 001               # append your result to leaderboard.yaml + PR instructions
  loop submissions [--all]      # the leaderboard
  loop config --handle you      # set your GitHub handle
  loop version

No server, no login — your GitHub handle is your identity and your own API keys do the work.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path

import yaml

import runner

ROOT = Path(__file__).resolve().parent
DOT = ROOT / ".loop"
CFG = DOT / "config.json"
LAST = DOT / "last_run.json"
PROVIDER_KEYS = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DARKBLOOM_API_KEY", "LLM_API_KEY"]


# ── config ────────────────────────────────────────────────────────────────
def cfg_load() -> dict:
    return json.loads(CFG.read_text()) if CFG.exists() else {}


def cfg_save(c: dict) -> None:
    DOT.mkdir(exist_ok=True)
    CFG.write_text(json.dumps(c, indent=2))


def resolve_handle(arg: str | None) -> str:
    h = arg or cfg_load().get("handle")
    if not h:
        sys.exit("No handle. Run `loop config --handle <your_github_handle>` first.")
    return h


def task_num(tid: str) -> str:
    return tid.split("_")[0]  # "001_fix_bugs" or "001" -> "001"


def load_tasks() -> list[dict]:
    return yaml.safe_load((ROOT / "tasks.yaml").read_text()) or []


def find_task(tid: str) -> dict:
    n = task_num(tid)
    for t in load_tasks():
        if task_num(t["id"]) == n:
            return t
    sys.exit(f"No task {tid!r}. Try `loop tasks`.")


def model_labels(agents: list[dict]) -> list[str]:
    out = []
    for a in agents:
        m, url = a["model"].lower(), a["base_url"].lower()
        if "haiku" in m: label = "Haiku"
        elif "opus" in m: label = "Opus"
        elif "sonnet" in m: label = "Sonnet"
        elif "darkbloom" in url: label = "Darkbloom"
        else: label = a["model"]
        if label not in out:
            out.append(label)
    return out


# ── commands ──────────────────────────────────────────────────────────────
def cmd_config(args):
    c = cfg_load()
    if args.handle:
        c["handle"] = args.handle
        cfg_save(c)
    print(f"handle:   {c.get('handle', '(unset — loop config --handle <you>)')}")
    keys = [k for k in PROVIDER_KEYS if os.environ.get(k)]
    print(f"api keys: {', '.join(keys) if keys else '(none in env — export your provider key)'}")
    print(f"repo:     {ROOT}")


def cmd_tasks(args):
    print("Loop Squad — pick a problem:\n")
    for t in load_tasks():
        print(f"  {task_num(t['id']):>3}  {t['title']:<12} [{t.get('difficulty','')}]  {t['blurb']}")
    print("\nRead one:   loop task <id>")
    print("Get going:  loop start <id> --handle <you>")


def cmd_task(args):
    t = find_task(args.id)
    d = sorted(ROOT.glob(f"tasks/{task_num(t['id'])}_*"))[0]
    print((d / "task.md").read_text())


def cmd_start(args):
    t = find_task(args.id)
    handle = resolve_handle(args.handle)
    arch = args.arch or t.get("starter", "supervisor")
    size = 5 if arch == "debate" else 3
    starter = ROOT / "starters" / f"{arch}_{size}.py"
    if not starter.exists():
        sys.exit(f"No starter {starter.name}. Starters: {[p.name for p in (ROOT/'starters').glob('*.py')]}")
    dest = ROOT / "submissions" / f"{handle}.py"
    if dest.exists() and not args.force:
        sys.exit(f"{dest.relative_to(ROOT)} already exists. Edit it, or pass --force to overwrite.")
    shutil.copy(starter, dest)
    cfg = cfg_load(); cfg["handle"] = handle; cfg_save(cfg)
    print(f"Scaffolded {dest.relative_to(ROOT)} from {starter.name} ({size}-agent {arch}).")
    print("Tune the prompts/models, then:")
    print(f"  loop run {task_num(t['id'])}          # add --mock for a keyless dry run")


def cmd_run(args):
    handle = resolve_handle(args.handle)
    sub = Path(args.submission) if args.submission else ROOT / "submissions" / f"{handle}.py"
    if not sub.exists():
        sys.exit(f"No submission {sub}. Run `loop start {task_num(args.id)} --handle {handle}`.")
    squad = runner.load_submission(sub)
    provider = runner.Provider(mock=runner._mock_provider() if args.mock else None)
    r = runner.run(task_num(args.id), sub, provider)
    runner.print_result(r, handle)
    t = find_task(args.id)
    DOT.mkdir(exist_ok=True)
    LAST.write_text(json.dumps({
        "task": t["id"], "solver": handle, "architecture": squad["architecture"],
        "squad_size": len(squad["agents"]), "models": model_labels(squad["agents"]),
        "solved": r["solved"], "cost": round(r["cost"], 4), "iterations": r["iterations"],
        "score": r["score"], "run_hash": r["run_hash"], "created": date.today().isoformat(),
        "mock": args.mock,
    }, indent=2))
    if r["solved"] and not args.mock:
        print("\nLooks good → `loop submit " + task_num(args.id) + "`")


def _row_yaml(r: dict) -> str:
    models = "[" + ", ".join(r["models"]) + "]"
    return (
        f"\n- task: {r['task']}\n"
        f"  solver: {r['solver']}\n"
        f"  architecture: {r['architecture']}\n"
        f"  squad_size: {r['squad_size']}\n"
        f"  models: {models}\n"
        f"  solved: true\n"
        f"  cost: {r['cost']}\n"
        f"  iterations: {r['iterations']}\n"
        f"  score: {r['score']}\n"
        f"  run_hash: {r['run_hash']}\n"
        f"  created: {r['created']}\n"
        f"  verified: self-reported\n"
    )


def cmd_submit(args):
    if not LAST.exists():
        sys.exit("No run to submit. Run `loop run <id>` first.")
    r = json.loads(LAST.read_text())
    if r.get("mock"):
        sys.exit("That was a --mock run (not a real solve). Run for real, then submit.")
    if not r["solved"]:
        sys.exit("Last run was not solved — nothing to submit.")
    if args.id and task_num(args.id) != task_num(r["task"]):
        sys.exit(f"Last run was {r['task']}, not {args.id}. Re-run the task you want to submit.")
    lb = ROOT / "leaderboard.yaml"
    lb.write_text(lb.read_text().rstrip() + "\n" + _row_yaml(r))
    shutil.copy(lb, ROOT / "docs" / "leaderboard.yaml")  # keep Pages board in sync (CI enforces)
    print(f"Appended your {r['task']} row (score {r['score']}) to leaderboard.yaml + docs/.")
    print("Validate, then open a PR:")
    print("  python verify_leaderboard.py")
    print(f"  git checkout -b loop/{r['solver']}-{task_num(r['task'])}")
    print(f"  git add submissions/{r['solver']}.py leaderboard.yaml docs/leaderboard.yaml")
    print(f"  git commit -m 'loop-squad: @{r['solver']} @ {r['task']} (score {r['score']})'")
    print(f"  gh pr create --fill")


def cmd_submissions(args):
    rows = yaml.safe_load((ROOT / "leaderboard.yaml").read_text()) or []
    handle = cfg_load().get("handle")
    if not args.all and handle:
        rows = [r for r in rows if r["solver"] == handle]
    if args.task:
        rows = [r for r in rows if task_num(r["task"]) == task_num(args.task)]
    rows.sort(key=lambda r: (r["task"], r["score"]))
    if not rows:
        print("No submissions." + ("" if args.all else "  (use --all to see everyone's)"))
        return
    print(f"{'TASK':<14}{'SOLVER':<14}{'SCORE':>6}  SQUAD           WHEN")
    for r in rows:
        squad = f"{r['squad_size']} {r['architecture'][:3]}"
        crown = "🏆 " if r == min([x for x in rows if x["task"] == r["task"]], key=lambda x: x["score"]) else "   "
        print(f"{task_num(r['task'])+' '+r['task'].split('_',1)[1]:<14}{crown}@{r['solver']:<10}{r['score']:>6}  {squad:<15} {r['created']}")


def cmd_version(args):
    print("loop 1.0.0  ·  Loop Squad — Eigen Builder Collective")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="loop", description="Loop Squad CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("config", help="show/set your handle and see provider keys")
    p.add_argument("--handle"); p.set_defaults(fn=cmd_config)

    sub.add_parser("tasks", help="list the problems").set_defaults(fn=cmd_tasks)

    p = sub.add_parser("task", help="print one problem")
    p.add_argument("id"); p.set_defaults(fn=cmd_task)

    p = sub.add_parser("start", help="scaffold a submission from a starter loop")
    p.add_argument("id"); p.add_argument("--handle"); p.add_argument("--arch")
    p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_start)

    p = sub.add_parser("run", help="run your squad against a task")
    p.add_argument("id"); p.add_argument("--submission"); p.add_argument("--handle")
    p.add_argument("--mock", action="store_true"); p.set_defaults(fn=cmd_run)

    p = sub.add_parser("submit", help="append your last run to the leaderboard")
    p.add_argument("id", nargs="?"); p.set_defaults(fn=cmd_submit)

    p = sub.add_parser("submissions", help="list leaderboard rows")
    p.add_argument("--all", action="store_true"); p.add_argument("--task")
    p.set_defaults(fn=cmd_submissions)

    sub.add_parser("version", help="print version").set_defaults(fn=cmd_version)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
