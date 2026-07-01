"""Starter loop — 3-agent supervisor (the Session 5 pattern). Good for 001 (fix_bugs).

A cheap executor does the work; a small smart supervisor audits and sends it back
until the verifier is happy. Copy to submissions/<your_handle>.py and run.
"""

SQUAD = {
    "architecture": "supervisor",
    "agents": [
        {
            "role": "planner",
            "prompt": "You plan the fix in 2-3 bullets. You do not write the solution.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
            "api_key_env": "ANTHROPIC_API_KEY",
        },
        {
            "role": "executor",
            "prompt": "You write the corrected file and emit it in the <<<FILE path=...>>> "
                      "block. Follow the plan and the supervisor feedback. No extra prose.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
        {
            "role": "supervisor",
            "prompt": "You audit the work against the task and the test feedback. Be specific "
                      "and terse about exactly what to change. Don't rewrite it yourself.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
            "api_key_env": "ANTHROPIC_API_KEY",
        },
    ],
}
