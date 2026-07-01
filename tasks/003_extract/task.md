# 003 — extract

Read the messy `invoice.txt` and emit a clean, structured `invoice.json` that matches
this schema exactly:

```json
{
  "vendor": "Acme Corp",
  "items": [
    {"desc": "Widget", "qty": 3, "unit_price": 9.99}
  ],
  "total": 181.47
}
```

Rules:
- `vendor` is the company on the `INVOICE — <vendor>` line.
- Each line item looks like `<qty> x <desc> @ $<unit_price>`. Capture every one, in order.
- `qty` is an integer; `unit_price` is a number (no `$`); `desc` is trimmed.
- **Ignore the "Printed total"** — it's stale. Compute `total` yourself as the sum of
  `qty * unit_price` over all items, rounded to 2 decimals.

Emit:

```
<<<FILE path=invoice.json>>>
{ ...your JSON... }
<<<END>>>
```

Difficulty: **medium** — the stale-total trap and multi-field extraction reward a
`debate` (5 agents) or a `manager` squad.
