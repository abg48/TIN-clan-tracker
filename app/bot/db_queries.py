from app.db.connection import get_connection
from datetime import datetime, timedelta

def get_member_total_xp(rsn):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT m.id, m.rsn, x.total_xp, x.timestamp
            FROM members m
            LEFT JOIN xp_snapshots x ON m.id = x.member_id
            WHERE m.rsn = ? COLLATE NOCASE AND x.id = (
                SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id
            )
            """,
            (rsn,)
        ).fetchone()
        return dict(row) if row else None
    
def get_all_member_xp():
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank, x.total_xp, x.timestamp
            FROM members m
            LEFT JOIN xp_snapshots x ON m.id = x.member_id
            WHERE m.active = 1 AND x.id = (
                SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id
            )
            ORDER BY x.total_xp DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]
    
def get_inactive_members():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 0 ORDER BY rsn"
        ).fetchall()
        return [dict(row) for row in rows]
    
def get_inactive_members_by_rank_and_days(rank, days):
    with get_connection() as conn:
        cutoff_date = datetime.now() - timedelta(days=days)
        rows = conn.execute(
            """
            SELECT m.id, m.rsn, m.rank,
                   latest.total_xp as current_xp,
                   latest.timestamp as current_timestamp,
                   old.total_xp as xp_at_cutoff,
                   old.timestamp as old_timestamp
            FROM members m
            LEFT JOIN xp_snapshots latest ON m.id = latest.member_id
                AND latest.id = (SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id)
            LEFT JOIN xp_snapshots old ON m.id = old.member_id
                AND old.timestamp <= ?
                AND old.id = (SELECT MAX(id) FROM xp_snapshots WHERE member_id = m.id AND timestamp <= ?)
            WHERE m.active = 0
            AND m.rank = ? COLLATE NOCASE
            AND latest.total_xp = old.total_xp
            ORDER BY latest.timestamp ASC
            """,
            (cutoff_date, cutoff_date, rank)
        ).fetchall()
        return [dict(row) for row in rows]
    
def get_members_by_rank(rank):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, rsn, rank FROM members WHERE active = 1 rank = ? ORDER BY rsn",
            (rank,)
        ).fetchall()
        return [dict(row) for row in rows]
    
def get_member_xp_history(rsn, days=7):
    with get_connection() as conn:
        cutoff_date = datetime.now() - timedelta(days=days)
        rows = conn.execute(
            """
            SELECT x.timestamp, x.total_xp
            FROM xp_snapshots x
            JOIN members m ON x.member_id = m.id
            WHERE m.rsn = ? COLLATE NOCASE AND x.timestamp >= ?
            ORDER BY x.timestamp
            """,
            (rsn, cutoff_date)
        ).fetchall()
        return [dict(row) for row in rows]