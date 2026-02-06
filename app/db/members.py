from app.db.connection import get_connection

def get_all_members():
    with get_connection() as conn:
        rows = conn.execute("SELECT id, rsn, rank, active FROM members").fetchall()
        return[dict(row) for row in rows]
    
def insert_member(rsn, rank):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO members (rsn, rank, active) VALUES (?, ?, 1)",(rsn, rank))

def mark_member_active(rsn):
    with get_connection() as conn:
        conn.execute("UPDATE members SET active = 1 WHERE rsn=?", (rsn,))

def mark_member_inactive(rsn):
    with get_connection() as conn:
        conn.execute("UPDATE members SET active = 0 WHERE rsn=?", (rsn,))

def update_member_rank(rsn, rank):
    with get_connection() as conn:
        conn.execute("UPDATE members SET rank=? WHERE rsn=? COLLATE NOCASE", (rank, rsn))
