# 001 — fix_bugs

`rle.py` is a run-length codec with **three bugs**. The intended behavior:

- `encode(s)` → `"aaabbc"` becomes `"3a2b1c"` (count, then character, per run).
- `decode(s)` → the exact inverse: `"3a2b1c"` becomes `"aaabbc"`.
- They must round-trip for any lowercase string: `decode(encode(s)) == s`.
- Counts can be **any length** — `encode("a" * 12) == "12a"` and `decode("12a") == "a" * 12`.

The three bugs: the first run is off by one, the last run is dropped, and multi-digit
counts break on decode. Find and fix all three.

Emit the corrected file:

```
<<<FILE path=rle.py>>>
...your fixed module...
<<<END>>>
```

Difficulty: **warmup** — a tight 3-agent `supervisor` squad on a cheap model.
