import requests
import sqlite3
import time
import random
from rs3clans import clans

DB = "/app/data/clan_tracker.db"

def main():
    
    sync_members()

    update_all_members()

# Given an RSN, query runemetrics API for that players total xp
# NOTE: Metrics API is notoriously finnicky. Some retry logic has been added to (hopefully) account for that
def get_total_xp(rsn):
    url = "https://apps.runescape.com/runemetrics/profile/profile"
    params = {"user": rsn, "activities": 1}
    delay = 2 # In seconds
    retries = 5 # If 5 retries reached, the profile is likely private

    for attempt in range(retries):
        try:
            r = requests.get(url, params=params, timeout=10)
            data = r.json()

            if "error" not in data:
                return int(data["totalxp"])
            
        except Exception as e:
            pass

        # Retry, exponential backoff
        sleep_time = delay + random.uniform(0, 1)
        print(f"{rsn}: retrying in {sleep_time:.1f}s")
        time.sleep(sleep_time)
        delay *= 2

    print(f"{rsn}: failed after retries")
    return None
    
# Update db with members current xp totals
def save_snapshot(member_id, total_xp):
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "INSERT INTO xp_snapshots (member_id, total_xp) VALUES (?, ?)",
            (member_id, total_xp)
        )

# Updates all active clan members xp totals
def update_all_members():
    with sqlite3.connect(DB) as conn:
        members = conn.execute("SELECT id, rsn FROM members WHERE active=1").fetchall()

    for member_id, rsn in members:
        xp = get_total_xp(rsn)
        if xp is not None:
            save_snapshot(member_id, xp)
            print(f"{rsn}: snapshot saved ({xp})")

# Updates db to reflect roster changes since last update
def sync_members():
    print("--- ROSTER UPDATES ---")

    clan = clans.Clan("The Iron Nation")
    live_members = {
        member.name: member.rank
        for member in clan
    }

    with sqlite3.connect(DB) as conn:
        rows = conn.execute("SELECT rsn, rank, active FROM members").fetchall()

    db_rsn_set = {row[0] for row in rows} # All members in db, active or otherwise
    active_db_set = {row[0] for row in rows if row[1] == 1} # Only active members in db
    inactive_db_set = {row[0] for row in rows if row[1] == 0} # Only inactive members in db
    db_rank_map = {row[0]: row[1] for row in rows} # Clan member ranks, for detecting changes in ranks

    new_members = live_members.keys() - db_rsn_set
    rejoining_members = live_members.keys() & inactive_db_set # Catches edge case of someone leaving & coming back
    departed_members = active_db_set - live_members.keys()
    active_members = live_members.keys() & active_db_set

    with sqlite3.connect(DB) as conn:
        for rsn in new_members:
            conn.execute("INSERT INTO members (rsn, rank, active) VALUES (?, ?, 1)", (rsn, live_members[rsn]))
            print("Added " + rsn + " to clan")

        for rsn in rejoining_members:
            conn.execute("UPDATE members SET active=1, rank=? WHERE rsn=? COLLATE NOCASE", (live_members[rsn], rsn))
            print("Added " + rsn + " to clan")

        for rsn in departed_members:
            conn.execute("UPDATE members SET active = 0 WHERE rsn=? COLLATE NOCASE", (rsn,))
            print("Removed " + rsn + " from clan")

        for rsn in active_members:
            live_rank = live_members[rsn]
            db_rank = db_rank_map.get(rsn)

            if live_rank != db_rank:
                conn.execute("UPDATE members SET rank=? WHERE rsn=? COLLATE NOCASE", (live_rank, rsn))
                print(rsn + " has ranked up! Was: " + db_rank + " now: " + live_rank)

if __name__ == "__main__":
    main()