from app.db.connection import get_connection

def save_snapshot(member_id, total_xp):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO xp_snapshots (member_id, total_xp) VALUES (?, ?)",
            (member_id, total_xp)
        )

def get_latest_snapshot(member_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM xp_snapshots WHERE member_id=? ORDER BY id DESC LIMIT 1",
            (member_id,)
        ).fetchone()
        return dict(row) if row else None