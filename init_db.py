import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    date TEXT NOT NULL,
    status TEXT NOT NULL
)
""")

conn.commit()
conn.close()
print("Attendance table ready")