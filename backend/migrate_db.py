import sqlite3
import os
import time

DB_PATH = "d:/steel/backend/sql_app.db"

def migrate():
    print(f"Checking database at {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(drawings)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "drawing_date" in columns:
            print("Column 'drawing_date' already exists. No action needed.")
        else:
            print("Adding column 'drawing_date'...")
            cursor.execute("ALTER TABLE drawings ADD COLUMN drawing_date VARCHAR")
            conn.commit()
            print("Migration successful!")
            
        conn.close()
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print("ERROR: Database is locked. Please STOP the backend server (Ctrl+C in terminal) and try again.")
        else:
            print(f"Operational Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    migrate()
