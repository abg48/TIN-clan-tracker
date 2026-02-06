from unittest.mock import patch
from app.main import update_all_members
from app.db.members import insert_member
from app.db.xp_snapshots import get_latest_snapshot
from app.db.schema import create_tables

@patch('app.main.fetch_total_xp')
def test_xp_sync_records_snapshot(mock_fetch_total_xp, temp_db):
    create_tables()

    insert_member('Alice', 'Recruit')

    mock_fetch_total_xp.return_value = 2_000_000

    update_all_members()

    snapshot = get_latest_snapshot(1)
    assert snapshot["total_xp"] == 2_000_000