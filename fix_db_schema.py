
import sqlite3
import os

def migrate():
    db_path = "backend/sql_app.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check users table
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns in 'users': {columns}")

    expected_users_columns = {
        "full_name": "TEXT",
        "is_active": "BOOLEAN DEFAULT 1",
        "hh_access_token": "TEXT",
        "hh_refresh_token": "TEXT"
    }

    for col, col_type in expected_users_columns.items():
        if col not in columns:
            print(f"Adding column '{col}' to 'users' table...")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except Exception as e:
                print(f"Error adding column {col}: {e}")

    # Check vacancies table (just in case)
    cursor.execute("PRAGMA table_info(vacancy)")
    vacancy_columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns in 'vacancy': {vacancy_columns}")

    expected_vacancy_columns = {
        "created_at": "DATETIME",
        "published_at": "DATETIME"
    }

    for col, col_type in expected_vacancy_columns.items():
        if col not in vacancy_columns:
            print(f"Adding column '{col}' to 'vacancy' table...")
            try:
                cursor.execute(f"ALTER TABLE vacancy ADD COLUMN {col} {col_type}")
            except Exception as e:
                print(f"Error adding column {col}: {e}")

    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
