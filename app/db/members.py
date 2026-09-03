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

def rename_member(old_rsn, new_rsn):
    """Rename a member while preserving their ID and XP history.
    
    Returns:
        tuple: (success: bool, message: str)
    """
    with get_connection() as conn:
        # Check if old_rsn exists
        old_member = conn.execute("SELECT id FROM members WHERE rsn=? COLLATE NOCASE", (old_rsn,)).fetchone()
        if not old_member:
            return False, f"Member **{old_rsn}** not found in database."
        
        # Check if new_rsn already exists
        new_member = conn.execute("SELECT id FROM members WHERE rsn=? COLLATE NOCASE", (new_rsn,)).fetchone()
        if new_member:
            return False, f"Member **{new_rsn}** already exists in database."
        
        # Update the RSN
        try:
            conn.execute("UPDATE members SET rsn=? WHERE rsn=? COLLATE NOCASE", (new_rsn, old_rsn))
            conn.commit()
            return True, f"Successfully renamed **{old_rsn}** → **{new_rsn}**. All XP history preserved."
        except Exception as e:
            return False, f"Error during rename: {e}"
