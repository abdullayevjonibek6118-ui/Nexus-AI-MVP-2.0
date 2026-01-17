
import sys
import os

# Add backend to python path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.db.init_db import init_db

if __name__ == "__main__":
    print("Initializing database from root...")
    init_db()
    print("Done.")
