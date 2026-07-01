"""End-to-end smoke test, no API keys. Uses a mock provider that actually solves 001.

Run: python -m pytest tests/ -q     (or just: python tests/test_smoke.py)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import runner
from loop_io import extract_files
from scorer import score

FIXED_RLE = """\
<<<FILE path=rle.py>>>
import re


def encode(s):
    if not s:
        return ""
    out = []
    count = 1
    prev = s[0]
    for ch in s[1:]:
        if ch == prev:
            count += 1
        else:
            out.append(str(count) + prev)
            prev = ch
            count = 1
    out.append(str(count) + prev)
    return "".join(out)


def decode(s):
    out = []
    for count, ch in re.findall(r"(\\d+)([a-z])", s):
        out.append(ch * int(count))
    return "".join(out)
<<<END>>>
"""


def solving_mock(role, messages):
    # every agent returns the fixed file; the executor's output is what gets verified
    return (FIXED_RLE, 120, 60)


def test_extract_files():
    files = extract_files(FIXED_RLE)
    assert "rle.py" in files and "def encode" in files["rle.py"]


def test_scorer():
    assert score(0.012, 4, 3) == 38


def test_solve_001_and_hash_is_deterministic():
    sub = ROOT / "submissions" / "aashatwt.py"
    r1 = runner.run("001", sub, runner.Provider(mock=solving_mock))
    r2 = runner.run("001", sub, runner.Provider(mock=solving_mock))
    assert r1["solved"] is True
    assert r1["iterations"] == 1            # solved on the first candidate
    assert r1["cost"] > 0
    assert r1["run_hash"] == r2["run_hash"]  # deterministic
    assert r1["architecture"] == "3-agent supervisor"


if __name__ == "__main__":
    test_extract_files()
    test_scorer()
    test_solve_001_and_hash_is_deterministic()
    print("smoke ok")
