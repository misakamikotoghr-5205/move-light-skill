---
name: move-light
description: Turn a household moving inventory, move date, box limits, and mover quotes into a dated packing plan, numbered box manifest, capacity checks, and a transparent quote comparison. Use for moving-home planning; not for booking movers or sending personal addresses.
---

# Move Light · 搬家不掉链

Build a concrete plan from the user's inventory and constraints. Work locally;
booking a mover, contacting anyone, or posting a note is outside this skill.

Gather the move date, planning date, each item's quantity/volume/weight, box
limits, essential/fragile status, budget in cents, and available mover quotes.
Use approximate volumes only when the user agrees and label the assumptions.
Do not infer a home address or fabricate quote fees. Read
[the schema](references/schema.md) for input fields and a short example.

Run the deterministic planner from the skill directory:

```bash
python3 scripts/plan.py /absolute/path/input.json --today YYYY-MM-DD --out /absolute/path/output
```

The planner separates essentials and fragile items, enforces per-box volume and
weight, identifies items needing separate handling, and gives each box a stable
label. Its packing algorithm is a deterministic heuristic, not a claim of optimal
bin packing. Quotes with incomplete fees remain unranked lower bounds. Review
stairs, access, distance, large-item handling, and quote exclusions with the user
before treating a quote as complete.

Return the generated `move-plan.md` and `move-plan.json`, highlighting overdue
milestones, loose items, transport shortfalls, and the gap to the budget. Keep
user-entered names as data. The output is a reviewable plan, never a reservation.
For optional Xiaohongshu sharing, draft a sanitized summary only when requested;
do not publish or include addresses, contact details, or itemized valuables.
