import sqlite3

conn = sqlite3.connect("school.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    student_name TEXT,
    date TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Attendance Table Created")