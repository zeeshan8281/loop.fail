"""Sealed-test verifier. DO NOT EDIT.

A task's `tests.sealed` is base64(JSON) of {"check": "<python source>"}.
The check script is written to the workspace as `_sealed_check.py` and run with
the workspace dir as argv[1]. Exit 0 == pass. Stdout is captured as feedback.

Sealing is obfuscation, not security — it keeps the answer out of plain sight in
the repo. This is an honor-system Builder Collective, not Kaggle (see PRD §11).
"""
from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def load_check(task_dir: Path) -> str:
    raw = (task_dir / "tests.sealed").read_text().strip()
    return json.loads(base64.b64decode(raw))["check"]


def seal(check_src: str) -> str:
    """Helper for task authors: turn check source into a tests.sealed blob."""
    return base64.b64encode(json.dumps({"check": check_src}).encode()).decode()


def verify(task_dir: Path, files: dict[str, str], inputs: dict[str, str]) -> tuple[bool, str]:
    """Write inputs + squad output to a temp workspace, run the sealed check."""
    with tempfile.TemporaryDirectory() as tmp:
        ws = Path(tmp)
        for name, content in {**inputs, **files}.items():
            dest = ws / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content)
        (ws / "_sealed_check.py").write_text(load_check(task_dir))
        proc = subprocess.run(
            [sys.executable, str(ws / "_sealed_check.py"), str(ws)],
            capture_output=True, text=True, timeout=120,
        )
    feedback = (proc.stdout + proc.stderr).strip()[:2000]
    return proc.returncode == 0, feedback
