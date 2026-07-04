import sqlite3

conn = sqlite3.connect("school.db")
cur = conn.cursor()

users = [
    ("admin", "admin123", "Admin"),
    ("faculty", "faculty123", "Faculty"),
    ("student", "student123", "Student")
]

cur.executemany(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    users
)

conn.commit()
conn.close()

print("Users added successfully")