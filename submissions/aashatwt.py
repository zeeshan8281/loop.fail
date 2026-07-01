"""Example leaderboard entry — a lean 3-agent supervisor squad on cheap models."""

SQUAD = {
    "architecture": "supervisor",
    "agents": [
        {
            "role": "planner",
            "prompt": "You plan the fix in two or three bullet points. You do not write code.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
        {
            "role": "executor",
            "prompt": "You write the corrected file. Emit it in the required FILE block. Nothing else.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
        {
            "role": "supervisor",
            "prompt": "You audit against the task and tests. Be specific and terse about fixes.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
    ],
}
