import sqlite3
import os

def migrate_single_db(db_path):
    if not os.path.exists(db_path):
        print(f"Skipping {db_path} (not found)")
        return

    print(f"Migrating {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE vacancy ADD COLUMN hh_id TEXT")
    except sqlite3.OperationalError as e:
        print(f"Vacancy (hh_id) note: {e}")
        
    try:
        cursor.execute("ALTER TABLE vacancy ADD COLUMN hh_status TEXT")
    except sqlite3.OperationalError as e:
        print(f"Vacancy (hh_status) note: {e}")

    try:
        cursor.execute("ALTER TABLE candidates ADD COLUMN hh_resume_id TEXT")
    except sqlite3.OperationalError as e:
        print(f"Candidates (hh_resume_id) note: {e}")

    try:
        cursor.execute("ALTER TABLE candidates ADD COLUMN screening_questions JSON")
    except sqlite3.OperationalError as e:
        print(f"Candidates (screening_questions) note: {e}")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
    except sqlite3.OperationalError as e:
        print(f"Users (full_name) note: {e}")

    conn.commit()
    conn.close()
    print(f"Migration complete for {db_path}.")

def migrate():
    possible_paths = ["backend/sql_app.db", "sql_app.db"]
    for path in possible_paths:
        migrate_single_db(path)

if __name__ == "__main__":
    migrate()
