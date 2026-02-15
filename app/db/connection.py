import os
import sqlite3
import zipfile
import time
from datetime import datetime

def get_connection():
    # Read DB path at call-time so test monkeypatching works correctly
    db_path = os.getenv("DB_PATH", "data/clan_tracker.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def backup_db():
    # Create backup directories if they don't exist
    db_path = os.getenv("DB_PATH", "data/clan_tracker.db")
    backup_dir = "data/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Build & implement timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_backup_path = f"{backup_dir}/temp_backup_{timestamp}.db"
    
    # Backup
    with sqlite3.connect(db_path) as source_conn, sqlite3.connect(temp_backup_path) as backup_conn:
        source_conn.backup(backup_conn)

    # Zip the temporary .db file
    zip_path = f"{backup_dir}/clan_tracker_backup_{timestamp}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(temp_backup_path, f"clan_tracker_backup_{timestamp}.db")

    # Clean temp files
    os.remove(temp_backup_path)

    print(f"Backup created: {zip_path}")

    # Ensure only the 30 most recent backups remain
    backup_files = [f for f in os.listdir(backup_dir) if f.startswith("clan_tracker_backup_") and f.endswith(".zip")]

    if len(backup_files) > 30:
        backup_files.sort(key=lambda f: os.path.getmtime(os.path.join(backup_dir, f)))

        for old_backup in backup_files[:-30]:
            os.remove(os.path.join(backup_dir, old_backup))
            print(f"Deleted old backup: {old_backup}")