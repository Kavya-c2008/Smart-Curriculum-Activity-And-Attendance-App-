import sqlite3

conn = sqlite3.connect("school.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT,
    name TEXT,
    department TEXT,
    year TEXT,
    email TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")