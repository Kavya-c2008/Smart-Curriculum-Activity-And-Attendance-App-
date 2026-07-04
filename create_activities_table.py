import sqlite3

conn = sqlite3.connect("school.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_name TEXT,
    activity_date TEXT,
    coordinator TEXT
)
""")

conn.commit()
conn.close()

print("Activities table created successfully!")