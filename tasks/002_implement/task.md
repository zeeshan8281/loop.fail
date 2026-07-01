# 002 — implement

Implement `calc(expr)` in `calc.py`: a small arithmetic expression evaluator.

Grammar (well-formed inputs only):
- Non-negative integer literals.
- Binary operators `+`, `-`, `*`, `/` with standard precedence (`*` and `/` bind tighter than `+` and `-`).
- Parentheses `(` `)`.
- Arbitrary whitespace between tokens.
- **No** unary minus; every intermediate and final result is a non-negative integer.
- `/` is **integer division, truncating toward zero** (`7 / 2 == 3`).
- `-` and `/` are **left-associative** (`10 - 2 - 3 == 5`).

Examples:
```
calc("2+3*4")        == 14
calc("(2+3)*4")      == 20
calc("10-2-3")       == 5
calc(" 7 + 8 / 2 ")  == 11
calc("100/(2+3)")    == 20
calc("(1+2)*(3+4)")  == 21
```

Emit:

```
<<<FILE path=calc.py>>>
def calc(expr): ...
<<<END>>>
```

Difficulty: **medium** — rewards a real planner. Try `sequential` or `manager`, 3 agents.
