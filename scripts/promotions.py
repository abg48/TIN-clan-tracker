import sqlite3

DB = "../data/clan_tracker.db"

RANK_THRESHOLDS = [
    ("Recruit", 0),
    ("Corporal", 10_000_000),
    ("Sergeant", 50_000_000),
    ("Lieutenant", 150_000_000),
    ("Captain", 300_000_000),
    ("General", 750_000_000),
]

promotion_query = """
SELECT m.rsn, m.rank, x.total_xp
FROM members m
JOIN (
    SELECT member_id, MAX(timestamp) as latest
    FROM xp_snapshots
    GROUP BY member_id
) latest_xp ON latest_xp.member_id = m.id
JOIN xp_snapshots x
    ON x.member_id = m.id AND x.timestamp = latest_xp.latest
WHERE m.active = 1
"""

with sqlite3.connect(DB) as conn:
    cursor = conn.cursor()
    cursor.execute(promotion_query)
    rows = cursor.fetchall()

rank_order = [r[0] for r in RANK_THRESHOLDS]
rank_xp = dict(RANK_THRESHOLDS)
eligible = []

for rsn, current_rank, total_xp in rows:
    
    # Skip if they're Admin, Owner, etc.
    if current_rank not in rank_order:
        continue
    
    current_index = rank_order.index(current_rank)

    # Skip if they are already General
    if current_index == len(rank_order) -1:
        continue

    eligible_rank = None

    # Check each successive rank to ensure skipped ranks are caught
    for higher_rank in rank_order[current_index + 1:]:
        required_xp = rank_xp[higher_rank]
        if total_xp >= required_xp:
            eligible_rank = higher_rank
        else:
            break

    if eligible_rank:
        eligible.append((rsn, current_rank, eligible_rank, total_xp))

print("\n=== Promotion Eligible Members ===\n")

for rsn, current_rank, next_rank, xp in sorted(eligible, key=lambda x: x[3], reverse=True):
    xp_formatted = "{:,}".format(xp)
    print(rsn + " is " + current_rank + " should be: " + next_rank + " (total xp: " + xp_formatted + ")")