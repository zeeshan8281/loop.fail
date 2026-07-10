"""002_implement — sequential 3, all Darkbloom gpt-oss-20b."""

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
            "role": "designer",
            "prompt": (
                "Design a tiny recursive-descent parser for calc(expr). Grammar: "
                "expr = term (('+'|'-') term)* ; term = factor (('*'|'/') factor)* ; "
                "factor = INT | '(' expr ')'. Integer division truncates toward zero "
                "(use int(a/b) NOT a//b, since // floors toward -inf; here inputs are "
                "non-negative so either works, but int(a/b) is safer). Left-associative "
                "via while-loops in expr/term. Tokenize by skipping whitespace, reading "
                "runs of digits as INT, single chars for + - * / ( ). Output: a short "
                "3-bullet plan. No code."
            ),
            **_DARKBLOOM,
        },
        {
            "role": "coder",
            "prompt": (
                "Write calc.py. Emit exactly one <<<FILE path=calc.py>>> block, then <<<END>>>. "
                "No prose outside the block. Use a recursive-descent parser with an index into "
                "a token list. Tokens: integers (as int) and the single chars '+','-','*','/','(',')'. "
                "Tokenize by scanning expr, skipping whitespace, grouping consecutive digits. "
                "Parser functions: parse_expr, parse_term, parse_factor. In parse_expr, "
                "loop while next token is '+' or '-' and combine left-associatively. Same in "
                "parse_term for '*' and '/'. In parse_factor, if next is '(' consume it, "
                "recurse into parse_expr, consume ')'; else consume an int. Use int(a/b) for "
                "division to truncate toward zero. Signature: def calc(expr: str) -> int. "
                "Verify: calc('2+3*4')==14, calc('(2+3)*4')==20, calc('10-2-3')==5, "
                "calc(' 7 + 8 / 2 ')==11, calc('100/(2+3)')==20, calc('(1+2)*(3+4)')==21, "
                "calc('2')==2, calc('7/2')==3, calc('8/3')==2."
            ),
            **_DARKBLOOM,
        },
        {
            "role": "checker",
            "prompt": (
                "Re-read the coder's calc.py. Mentally evaluate every case: "
                "'2+3*4'->14, '(2+3)*4'->20, '10-2-3'->5, ' 7 + 8 / 2 '->11, '100/(2+3)'->20, "
                "'(1+2)*(3+4)'->21, '2'->2, '2*3*4'->24, '7/2'->3, '1+1+1+1'->4, '8/3'->2. "
                "If all match, re-emit the file unchanged in a single "
                "<<<FILE path=calc.py>>>...<<<END>>> block. If any is wrong, emit a fixed "
                "version in the same block. No prose."
            ),
            **_DARKBLOOM,
        },
    ],
}
