"""Starter loop — 3-agent sequential. Cheapest, tightest. Good for 002 (implement).

Copy to submissions/<your_handle>.py, tweak prompts, run:
  python runner.py --task 002 --submission submissions/<your_handle>.py
"""

SQUAD = {
    "architecture": "sequential",
    "agents": [
        {
            "role": "reader",
            "prompt": "You read the task and input files and restate, in 2-3 bullets, exactly "
                      "what the output file must contain. You write no code.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
        {
            "role": "coder",
            "prompt": "You write the complete solution and emit it in the required "
                      "<<<FILE path=...>>> block. No prose outside the block.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
        {
            "role": "checker",
            "prompt": "You re-read the task and the coder's file. If it satisfies every rule, "
                      "re-emit it unchanged in the FILE block. If not, fix it and emit the fix.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
    ],
}
