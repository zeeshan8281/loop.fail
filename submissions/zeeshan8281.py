"""zeeshan8281 — 3-agent supervisor, Claude Haiku via Claude Code."""

SQUAD = {
    "architecture": "supervisor",
    "agents": [
        {
            "role": "planner",
            "prompt": "You plan the bug fix in 2-3 terse bullets. You do not write code. Do not use any tools.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
        {
            "role": "executor",
            "prompt": "You write the corrected file and emit it ONLY as a <<<FILE path=...>>> ... <<<END>>> "
                      "block. No prose, no tools.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
        {
            "role": "supervisor",
            "prompt": "You audit the file against the task and test feedback. Be terse and specific about the fix. Do not use tools.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
    ],
}
