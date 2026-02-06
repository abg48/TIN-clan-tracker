from app.db.connection import get_connection

def create_tables():

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rsn TEXT UNIQUE COLLATE NOCASE,
                rank TEXT,
                active INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS xp_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_xp INTEGER,
                FOREIGN KEY(member_id) REFERENCES members(id)
            )
        ''')

        conn.commit()