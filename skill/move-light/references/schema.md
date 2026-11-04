# Planner input

Required: `move_date` (ISO date), `budget_fen` (nonnegative integer),
`box_capacity_l` and `box_max_weight_kg` (positive numbers), and `items` (list).
Each item has a unique `id`, `name`, integer `quantity` (1–100), positive
`volume_l`, nonnegative `weight_kg`, boolean `fragile`, and boolean `essential`.
Volume and weight are per unit, not the combined quantity. Maximum 1,000 units.

Optional `quotes`: list with unique `id`, `name`, nonnegative integer
`base_fen`, `per_box_fen`, `extra_fees_fen`; boolean `fees_complete`; and optional
`capacity_l` (positive number). Fee completeness is the user's assertion after
checking exclusions. `extra_fees_fen` is the quoted combined stairs, distance,
large-item, or other fees; unknown fees mean `fees_complete: false`.

```json
{"move_date":"2026-11-20","budget_fen":100000,"box_capacity_l":40,
 "box_max_weight_kg":15,"items":[{"id":"books","name":"书籍",
 "quantity":3,"volume_l":8,"weight_kg":5,"fragile":false,"essential":false}],
 "quotes":[{"id":"a","name":"示例报价","base_fen":30000,
 "per_box_fen":1000,"extra_fees_fen":5000,"fees_complete":true,"capacity_l":1000}]}
```

Use `--today` for reproducible examples. Output deadlines retain the original
milestone dates, so past work remains visibly overdue rather than silently moving.
All outputs are local. No geocoding, pricing lookup, or actual mover is contacted.
