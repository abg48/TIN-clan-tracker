import os
import sqlite3

def get_connection():
    # Read DB path at call-time so test monkeypatching works correctly
    db_path = os.getenv("DB_PATH", "data/clan_tracker.db")

    print("Opening DB:" + db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn