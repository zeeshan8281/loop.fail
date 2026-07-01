"""Copy me to submissions/<your_github_handle>.py and fill in your squad.

Rules:
  - Squad size must be exactly 3, 5, or 7.
  - architecture is one of: sequential, debate, supervisor, manager.
  - Each agent declares `pricing` in $/1,000,000 tokens so cost is computable.
  - Any OpenAI-compatible endpoint is allowed (set the matching API key env var).

Run it:
  export OPENAI_API_KEY=...          # or your provider's key (see api_key_env)
  python runner.py --task 001 --submission submissions/<your_handle>.py
"""

SQUAD = {
    "architecture": "supervisor",
    "agents": [
        {
            "role": "planner",
            "prompt": "You plan the work. You do not execute it. Be brief.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
            # "api_key_env": "ANTHROPIC_API_KEY",  # defaults to OPENAI_API_KEY / LLM_API_KEY
        },
        {
            "role": "executor",
            "prompt": "You execute the plan. Emit the corrected files. Be precise.",
            "model": "qwen3.5-27b",
            "base_url": "https://api.darkbloom.dev/v1",
            "pricing": {"in": 0.10, "out": 0.78},
            "api_key_env": "DARKBLOOM_API_KEY",
        },
        {
            "role": "supervisor",
            "prompt": "You audit the work against the task. Say exactly what to fix.",
            "model": "claude-haiku-4-5",
            "base_url": "https://api.anthropic.com/v1",
            "pricing": {"in": 1.00, "out": 5.00},
        },
    ],
}
