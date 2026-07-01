"""zeeshan8281 — 3-agent supervisor, GLM 5.2 via OpenRouter."""

_MODEL = "z-ai/glm-5.2"
_BASE = "https://openrouter.ai/api/v1"
_PRICING = {"in": 0.93, "out": 3.00}  # real OpenRouter $/1M for z-ai/glm-5.2
_KEY = "OPENROUTER_API_KEY"

SQUAD = {
    "architecture": "supervisor",
    "agents": [
        {
            "role": "planner",
            "prompt": "You plan the bug fix in 2-3 terse bullets. You do not write code. Do not use any tools.",
            "model": _MODEL, "base_url": _BASE, "pricing": _PRICING, "api_key_env": _KEY,
        },
        {
            "role": "executor",
            "prompt": "You write the corrected file and emit it ONLY as a <<<FILE path=...>>> ... <<<END>>> "
                      "block. No prose, no tools.",
            "model": _MODEL, "base_url": _BASE, "pricing": _PRICING, "api_key_env": _KEY,
        },
        {
            "role": "supervisor",
            "prompt": "You audit the file against the task and test feedback. Be terse and specific about the fix. Do not use tools.",
            "model": _MODEL, "base_url": _BASE, "pricing": _PRICING, "api_key_env": _KEY,
        },
    ],
}
