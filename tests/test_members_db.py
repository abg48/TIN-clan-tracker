from app.db.schema import create_tables
from app.db.members import (
    get_all_members, 
    insert_member, 
    mark_member_active, 
    mark_member_inactive, 
    update_member_rank,
)


def test_insert_member(temp_db):
    create_tables()

    insert_member("Alice", "Recruit")
    insert_member("Bob", "Corporal")

    members = get_all_members()
    rsns = {member['rsn'] for member in members}

    assert "Alice" in rsns
    assert "Bob" in rsns

def test_mark_member_inactive(temp_db):
    create_tables()

    insert_member("Charlie", "Recruit")
    mark_member_inactive("Charlie")

    members = get_all_members()
    charlie = next(member for member in members if member['rsn'] == "Charlie")

    assert charlie['active'] == 0

def test_mark_member_active(temp_db):
    create_tables()

    insert_member("Dave", "Recruit")
    mark_member_inactive("Dave")
    mark_member_active("Dave")

    members = get_all_members()
    dave = next(member for member in members if member['rsn'] == "Dave")

    assert dave['active'] == 1

def test_update_member_rank(temp_db):
    create_tables()

    insert_member("Eve", "Recruit")
    update_member_rank("Eve", "Sergeant")

    members = get_all_members()
    eve = next(member for member in members if member['rsn'] == "Eve")

    assert eve['rank'] == "Sergeant"