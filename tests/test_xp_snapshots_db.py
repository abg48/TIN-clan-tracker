from app.db.members import insert_member
from app.db.xp_snapshots import save_snapshot, get_latest_snapshot
from app.db.schema import create_tables

def test_save_and_get_snapshot(temp_db):
    create_tables()

    insert_member("Alice", "Recruit")
    
    save_snapshot(1, 1_000_000)
    save_snapshot(1, 1_500_000)

    latest = get_latest_snapshot(1)

    assert latest['total_xp'] == 1_500_000