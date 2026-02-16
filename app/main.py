import os
import requests
import sqlite3
import time
import random
from dotenv import load_dotenv

load_dotenv()
from app.db.members import get_all_members, insert_member, mark_member_active, mark_member_inactive, update_member_rank
from app.db.xp_snapshots import save_snapshot
from app.external.runemetrics import fetch_total_xp
from app.db.schema import create_tables
from app.db.connection import backup_db
from rs3clans import clans

def main():
    create_tables()
    sync_members()
    update_all_members()
    backup_db()

# Updates db to reflect roster changes since last update
def sync_members():
    print("--- ROSTER UPDATES ---")

    clan_name = os.getenv("CLAN_NAME", "The Iron Nation")
    clan = clans.Clan(clan_name)
    live_members = {member.name: member.rank for member in clan}
    live_rsns = set(live_members)

    members = get_all_members()
    db_rsns = {member['rsn'] for member in members} # All members in db, active or otherwise
    active_rsns = {member['rsn'] for member in members if member['active'] == 1} # Only active members in db
    inactive_rsns = {member['rsn'] for member in members if member['active'] == 0} # Only inactive members in db
    db_rank_map = {member['rsn']: member['rank'] for member in members} # Clan member ranks, for detecting changes in ranks

    new_members = live_rsns - db_rsns
    rejoining_members = live_rsns & inactive_rsns # Catches edge case of someone leaving & coming back
    departed_members = active_rsns - live_rsns
    active_members = live_rsns & active_rsns

    for rsn in new_members:
        insert_member(rsn, live_members[rsn])
        print(f"Added {rsn} to clan")

    for rsn in rejoining_members:
        mark_member_active(rsn)
        update_member_rank(rsn, live_members[rsn])
        print(f"Added {rsn} to clan")

    for rsn in departed_members:
        mark_member_inactive(rsn)
        print(f"Removed {rsn} from clan")

    for rsn in active_members:
        live_rank = live_members[rsn]
        db_rank = db_rank_map.get(rsn)

        if live_rank != db_rank:
            update_member_rank(rsn, live_rank)
            print(rsn + " has ranked up! Was: " + db_rank + " now: " + live_rank)

# Updates all active clan members xp totals
def update_all_members():
    print("--- UPDATING XP TOTALS ---")

    members = get_all_members()
    active_members = [member for member in members if member['active'] == 1]

    for member in active_members:
        member_id = member['id']
        rsn = member['rsn']
        xp = fetch_total_xp(rsn)
        if xp is not None:
            save_snapshot(member_id, xp)
            print(f"{rsn}: snapshot saved ({xp})")

if __name__ == "__main__":
    main()