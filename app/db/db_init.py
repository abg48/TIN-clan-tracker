import sqlite3

DB = "clan_tracker.db"

schema = """
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rsn TEXT UNIQUE COLLATE NOCASE,
    rank TEXT,
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS xp_snapshots(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_xp INTEGER,
    FOREIGN KEY(member_id) REFERENCES members(id)
);

CREATE TABLE IF NOT EXISTS inactivity_flags (
    member_id INTEGER,
    flagged_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    FOREIGN KEY(member_id) REFERENCES members(id)
);
"""

with sqlite3.connect(DB) as conn:
    conn.executescript(schema)