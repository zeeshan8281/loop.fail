"""Starter loop — 5-agent debate. For harder reasoning/extraction: 003 (extract).

Four solvers answer, see each other, and revise; a moderator merges the best into
the final file. Costs more (5 agents, more tokens) — only worth it when 3 can't crack it.
Copy to submissions/<your_handle>.py and run.
"""

_solver = {
    "prompt": "You solve the task and emit the output file in the <<<FILE path=...>>> block. "
              "When you see other agents' answers, keep what's right and fix what's wrong.",
    "model": "qwen3.5-27b",
    "base_url": "https://api.darkbloom.dev/v1",
    "pricing": {"in": 0.10, "out": 0.78},
    "api_key_env": "DARKBLOOM_API_KEY",
}

SQUAD = {
    "architecture": "debate",
    "agents": [
        {"role": "solver_a", **_solver},
        {"role": "solver_b", **_solver},
        {"role": "solver_c", **_solver},
        {"role": "solver_d", **_solver},
        {
            "role": "moderator",
            "prompt": "You are the moderator. Read the revised answers, pick or merge the correct "
                      "one, and emit the final output file in the <<<FILE path=...>>> block.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
            "api_key_env": "ANTHROPIC_API_KEY",
        },
    ],
}
