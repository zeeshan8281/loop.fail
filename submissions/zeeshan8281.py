"""zeeshan8281 — 3-agent supervisor, GLM-4.6 via OpenRouter."""

_MODEL = "z-ai/glm-4.6"                # glm-5.2 is not a real OpenRouter slug; 4.6 is the current GLM
_BASE = "https://openrouter.ai/api/v1"
_PRICING = {"in": 0.40, "out": 1.75}  # z-ai/glm-4.6 $/1M — verify the live rate at openrouter.ai/models
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
