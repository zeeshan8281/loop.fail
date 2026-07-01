"""Run-length codec. `encode('aaabbc') -> '3a2b1c'` and `decode` is its inverse.

Three bugs live in here — one breaks the first run, one drops the last run, one
breaks any count of 10 or more. Fix all three so encode/decode round-trip.
"""


def encode(s):
    if not s:
        return ""
    out = []
    count = 0
    prev = s[0]
    for ch in s[1:]:
        if ch == prev:
            count += 1
        else:
            out.append(str(count) + prev)
            prev = ch
            count = 1
    return "".join(out)


def decode(s):
    import re
    out = []
    for count, ch in re.findall(r"(\d)([a-z])", s):
        out.append(ch * int(count))
    return "".join(out)
