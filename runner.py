"""Loop Squad runner — the bounded loop. DO NOT EDIT.

  python runner.py --task 001 --submission submissions/<handle>.py

Implements the three Session 5 lessons literally:
  - the pattern: act -> observe -> learn -> repeat (architectures/)
  - the supervisor: the verifier judges; agents don't get to grade themselves
  - the kill switch: EVERY loop is bounded by meta.yaml caps (iters/tokens/wallclock)
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import os
import sys
import time
from pathlib import Path

import yaml

import verifier
from architectures import ARCHITECTURES
from scorer import score

ROOT = Path(__file__).parent


class CapReached(Exception):
    """Kill switch tripped — a bound in meta.yaml was hit."""


class Provider:
    """OpenAI-compatible chat client with per-agent pricing and usage tracking."""

    def __init__(self, mock=None):
        self._mock = mock  # callable(role, messages) -> str, for offline/CI
        self.cost = 0.0
        self.tokens = 0
        self._client_cache: dict[str, object] = {}

    def _client(self, base_url: str, api_key_env: str):
        if base_url not in self._client_cache:
            from openai import OpenAI  # lazy: not needed in mock mode
            key = os.environ.get(api_key_env) or os.environ.get("LLM_API_KEY", "")
            if not key:
                raise SystemExit(
                    f"No API key. Set {api_key_env} (or LLM_API_KEY) for {base_url}."
                )
            self._client_cache[base_url] = OpenAI(base_url=base_url, api_key=key)
        return self._client_cache[base_url]

    def call(self, agent: dict, messages: list[dict]) -> str:
        if self._mock is not None:
            text, pt, ct = self._mock(agent["role"], messages)
        else:
            client = self._client(agent["base_url"], agent.get("api_key_env", "OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model=agent["model"], messages=messages,
                temperature=0, seed=0,  # determinism (best-effort across providers)
            )
            # OpenRouter (and some gateways) return errors as a 200 body with no choices,
            # sometimes null usage, and reasoning models can leave content empty.
            choices = getattr(resp, "choices", None)
            if not choices:
                err = getattr(resp, "error", None) or getattr(resp, "model_extra", {}).get("error")
                raise SystemExit(f"{agent['model']} @ {agent['base_url']} returned no choices — "
                                 f"check the model id and your key. Provider said: {err or resp}")
            msg = choices[0].message
            text = msg.content or getattr(msg, "reasoning", None) or ""
            usage = getattr(resp, "usage", None)
            pt = getattr(usage, "prompt_tokens", 0) or 0
            ct = getattr(usage, "completion_tokens", 0) or 0
        p = agent["pricing"]
        self.cost += (pt * p["in"] + ct * p["out"]) / 1_000_000  # pricing is $/1M tokens
        self.tokens += pt + ct
        return text


class Context:
    """Handed to an architecture. Owns the kill switch and the loop bookkeeping."""

    def __init__(self, task_id, task_text, inputs, agents, provider, task_dir, meta):
        self.task = task_text
        self.inputs = inputs
        self.agents = agents
        self._p = provider
        self._task_dir = task_dir
        self._meta = meta
        self._start = time.monotonic()
        self.iterations = 0
        self.solved = False
        self.final_files: dict[str, str] = {}

    def should_continue(self) -> bool:
        return (
            self.iterations < self._meta["max_iterations"]
            and self._p.tokens < self._meta["max_tokens"]
            and (time.monotonic() - self._start) < self._meta["max_wallclock_s"]
        )

    def _guard(self):
        if self._p.tokens >= self._meta["max_tokens"]:
            raise CapReached("token cap")
        if (time.monotonic() - self._start) >= self._meta["max_wallclock_s"]:
            raise CapReached("wallclock cap")

    def agent(self, i: int, user_msg: str) -> str:
        """One LLM turn for agent[i % squad_size]. Counts toward cost/token caps."""
        self._guard()
        a = self.agents[i % len(self.agents)]
        return self._p.call(a, [
            {"role": "system", "content": a["prompt"]},
            {"role": "user", "content": user_msg},
        ])

    def context_blob(self) -> str:
        files = "\n\n".join(f"### {n}\n```\n{c}\n```" for n, c in self.inputs.items())
        return (
            f"{self.task}\n\n--- INPUT FILES ---\n{files}\n\n"
            "Emit each output file as:\n<<<FILE path=NAME>>>\n...content...\n<<<END>>>"
        )

    def verify(self, files: dict[str, str]) -> tuple[bool, str]:
        """Submit a candidate. Counts an iteration. The kill switch lives here too."""
        if not self.should_continue():
            raise CapReached("iteration cap")
        self.iterations += 1
        self.final_files = files or self.final_files
        passed, feedback = verifier.verify(self._task_dir, files, self.inputs)
        if passed:
            self.solved = True
        return passed, feedback


def load_submission(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("submission", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    squad = getattr(mod, "SQUAD", None)
    if not isinstance(squad, dict):
        raise SystemExit("Submission must export a SQUAD dict.")
    agents = squad.get("agents", [])
    if len(agents) not in (3, 5, 7):
        raise SystemExit(f"Squad size must be 3, 5, or 7 (got {len(agents)}).")
    if squad.get("architecture") not in ARCHITECTURES:
        raise SystemExit(f"architecture must be one of {sorted(ARCHITECTURES)}.")
    for a in agents:
        missing = {"role", "prompt", "model", "base_url", "pricing"} - set(a)
        if missing:
            raise SystemExit(f"Agent missing fields: {missing}")
        if not {"in", "out"} <= set(a["pricing"]):
            raise SystemExit("Each agent.pricing needs 'in' and 'out' ($/1M tokens).")
    return squad


def load_task(task_id: str):
    matches = sorted(ROOT.glob(f"tasks/{task_id}_*"))
    if not matches:
        raise SystemExit(f"No task {task_id} under tasks/.")
    d = matches[0]
    meta = yaml.safe_load((d / "meta.yaml").read_text())
    task_text = (d / "task.md").read_text()
    inputs = {p.name: p.read_text() for p in (d / "inputs").glob("*") if p.is_file()}
    return d, d.name, task_text, inputs, meta


def run_hash(task_name, submission_path, solved, iterations, files) -> str:
    sub_sha = hashlib.sha256(submission_path.read_bytes()).hexdigest()
    answer = "\n".join(f"{k}\n{files[k]}" for k in sorted(files))  # normalized
    blob = f"{task_name}|{sub_sha}|{solved}|{iterations}|{answer}"
    return hashlib.sha256(blob.encode()).hexdigest()


def run(task_id: str, submission_path: Path, provider: Provider) -> dict:
    task_dir, task_name, task_text, inputs, meta = load_task(task_id)
    squad = load_submission(submission_path)
    ctx = Context(task_id, task_text, inputs, squad["agents"], provider, task_dir, meta)
    arch = ARCHITECTURES[squad["architecture"]]
    t0 = time.monotonic()
    try:
        arch(ctx)
    except CapReached:
        pass  # kill switch tripped — keep whatever the last candidate was
    wall = time.monotonic() - t0
    s = score(provider.cost, ctx.iterations, len(squad["agents"]))
    rh = run_hash(task_name, submission_path, ctx.solved, ctx.iterations, ctx.final_files)
    arch_label = f"{len(squad['agents'])}-agent {squad['architecture']}"
    return {
        "task": task_name, "architecture": arch_label, "solved": ctx.solved,
        "cost": provider.cost, "iterations": ctx.iterations, "wallclock": wall,
        "score": s, "run_hash": rh,
    }


def print_result(r: dict, handle: str) -> None:
    line = "─" * 37
    print(f"\n── result ──{line[11:]}")
    print(f"task:         {r['task']}")
    print(f"solver:       @{handle}")
    print(f"architecture: {r['architecture']}")
    print(f"solved:       {'yes' if r['solved'] else 'no'}")
    print(f"cost:         ${r['cost']:.4f}")
    print(f"iterations:   {r['iterations']}")
    print(f"wallclock:    {r['wallclock']:.0f}s")
    print(f"score:        {r['score']}")
    print(f"run_hash:     {r['run_hash']}")
    print(line + "──")
    if not r["solved"]:
        print("NOTE: not solved — this run does not count on the leaderboard.")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True)
    ap.add_argument("--submission", required=True, type=Path)
    ap.add_argument("--mock", action="store_true", help="offline fake provider (CI/dev)")
    args = ap.parse_args(argv)
    provider = Provider(mock=_mock_provider() if args.mock else None)
    r = run(args.task, args.submission, provider)
    handle = args.submission.stem
    print_result(r, handle)
    return 0 if r["solved"] else 1


def _mock_provider():
    """Deterministic offline provider: echoes a trivial wrong answer.

    Real solving needs a real model. This only exercises the loop/score/hash path
    so CI can smoke-test runner.py without API keys (see tests/test_smoke.py for a
    mock that actually solves task 001)."""
    def fake(role, messages):
        return ("<<<FILE path=noop.txt>>>\n\n<<<END>>>", 100, 50)
    return fake


if __name__ == "__main__":
    sys.exit(main())
