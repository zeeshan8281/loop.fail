"""001_fix_bugs — sequential 3, all Darkbloom. Aim: one-shot, ~$0.001, score ~12."""

_DARKBLOOM = {
    "model": "gpt-oss-20b",
    "base_url": "https://api.darkbloom.dev/v1",
    "pricing": {"in": 0.10, "out": 0.78},
    "api_key_env": "DARKBLOOM_API_KEY",
}

SQUAD = {
    "architecture": "sequential",
    "agents": [
        {
            "role": "diagnoser",
            "prompt": (
                "You are given rle.py with three bugs. State each bug and its one-line fix. "
                "The bugs are: (1) the first run never emits — the initial count starts at 0 "
                "and prev is set before the loop, so the first character is never counted; "
                "(2) after the loop the final run is never appended; (3) decode uses \\d "
                "which matches a single digit, breaking counts of 10+. "
                "Emit only: three bullets, one per bug, each naming the fix. No code."
            ),
            **_DARKBLOOM,
        },
        {
            "role": "coder",
            "prompt": (
                "Write the corrected rle.py. Emit exactly one <<<FILE path=rle.py>>> block "
                "containing the full module, and <<<END>>>. No prose. "
                "Requirements: encode('') == ''; encode('a') == '1a'; encode('aaabbc') == '3a2b1c'; "
                "encode('a'*12) == '12a'; decode('12a') == 'a'*12; decode(encode(s)) == s for any "
                "lowercase s. Use re.findall(r'(\\d+)([a-z])', s) in decode. In encode, start with "
                "count=1 for s[0] and append the final run after the loop."
            ),
            **_DARKBLOOM,
        },
        {
            "role": "checker",
            "prompt": (
                "Re-read the coder's rle.py. Mentally run these six checks: "
                "encode('') == '', encode('a') == '1a', encode('aaabbc') == '3a2b1c', "
                "encode('a'*12) == '12a', decode('12a') == 'a'*12, decode(encode('abcabc')) == 'abcabc'. "
                "If all pass, re-emit the file unchanged in a single <<<FILE path=rle.py>>>...<<<END>>> "
                "block. If any fails, emit a corrected file in the same block. No prose."
            ),
            **_DARKBLOOM,
        },
    ],
}
