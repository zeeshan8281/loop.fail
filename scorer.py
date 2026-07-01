"""Loop Squad scoring. DO NOT EDIT.

score = cost_usd * 1000 + iterations * 5 + squad_size * 2   (lower wins)
"""
from __future__ import annotations


def score(total_cost_usd: float, iterations: int, squad_size: int) -> int:
    return round(total_cost_usd * 1000 + iterations * 5 + squad_size * 2)


def _demo() -> None:
    # cost dominates; squad bloat and iterations are tie-breakers
    assert score(0.012, 4, 3) == round(0.012 * 1000 + 20 + 6) == 38
    assert score(0.0, 0, 3) == 6
    # a 3-agent squad has a 10-pt head start over a 7-agent one, all else equal
    assert score(0.05, 4, 7) - score(0.05, 4, 3) == 8  # (7-3)*2
    print("scorer ok")


if __name__ == "__main__":
    _demo()
