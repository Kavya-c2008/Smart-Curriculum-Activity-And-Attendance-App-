from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from datetime import datetime
import qrcode
import os

app = Flask(__name__)
app.secret_key = "smart_curriculum_secret"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("school.db")
    return conn


# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        SELECT role FROM users
        WHERE username=? AND password=?
        """, (username, password))

        user = cur.fetchone()
        conn.close()

        if user:
            session['role'] = user[0]

            if user[0] == "Admin":
                return redirect('/admin_dashboard')
            elif user[0] == "Faculty":
                return redirect('/faculty_dashboard')
            elif user[0] == "Student":
                return redirect('/student_dashboard')

        return "Invalid Login"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cur.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        total_students=total_students,
        total_attendance=total_attendance
    )


# ---------------- ROLE DASHBOARDS ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin':
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM activities")
    total_activities = cur.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        total_students=total_students,
        total_attendance=total_attendance,
        total_activities=total_activities
    )

@app.route('/faculty_dashboard')
def faculty_dashboard():
    if session.get('role') != 'Faculty':
        return redirect('/')
    return render_template("faculty_dashboard.html")


@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'Student':
        return redirect('/')
    return render_template("student_dashboard.html")


# ---------------- ATTENDANCE ----------------
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        date = request.form['date']
        status = request.form['status']

        cur.execute("""
        INSERT INTO attendance (student_id, student_name, date, status)
        VALUES (?, ?, ?, ?)
        """, (student_id, student_name, date, status))

        conn.commit()
        conn.close()
        return redirect('/attendance')

    cur.execute("SELECT * FROM attendance")
    records = cur.fetchall()
    conn.close()

    return render_template("attendance.html", records=records)


# ---------------- ACTIVITIES ----------------
@app.route('/activities', methods=['GET', 'POST'])
def activities():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        activity_name = request.form['activity_name']
        activity_date = request.form['activity_date']
        coordinator = request.form['coordinator']

        cur.execute("""
        INSERT INTO activities (activity_name, activity_date, coordinator)
        VALUES (?, ?, ?)
        """, (activity_name, activity_date, coordinator))

        conn.commit()

    cur.execute("SELECT * FROM activities")
    activities = cur.fetchall()
    conn.close()

    return render_template("activities.html", activities=activities)


# ---------------- REGISTER STUDENT ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        department = request.form['department']
        year = request.form['year']
        email = request.form['email']

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            name TEXT,
            department TEXT,
            year TEXT,
            email TEXT
        )
        """)

        cur.execute("""
        INSERT INTO students (student_id, name, department, year, email)
        VALUES (?, ?, ?, ?, ?)
        """, (student_id, name, department, year, email))

        conn.commit()
        conn.close()

        return "Student Registered Successfully"

    return render_template("register.html")


# ---------------- VIEW STUDENTS ----------------
@app.route('/students')
def students():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    conn.close()
    return render_template("students.html", students=students)


# ---------------- DELETE STUDENT ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/students')


# ---------------- EDIT STUDENT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        student_id = request.form['student_id']
        name = request.form['name']
        department = request.form['department']
        year = request.form['year']
        email = request.form['email']

        cur.execute("""
        UPDATE students
        SET student_id=?, name=?, department=?, year=?, email=?
        WHERE id=?
        """, (student_id, name, department, year, email, id))

        conn.commit()
        conn.close()
        return redirect('/students')

    cur.execute("SELECT * FROM students WHERE id=?", (id,))
    student = cur.fetchone()

    conn.close()
    return render_template("edit_student.html", student=student)


# ---------------- EXPORT EXCEL ----------------
@app.route('/export_excel')
def export_excel():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT student_id, student_name, date, status FROM attendance")
    records = cur.fetchall()

    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    ws.append(["Student ID", "Student Name", "Date", "Status"])

    for row in records:
        ws.append(row)

    file = "attendance.xlsx"
    wb.save(file)

    return send_file(file, as_attachment=True)


# ---------------- EXPORT PDF ----------------
@app.route('/export_pdf')
def export_pdf():
    file = "attendance.pdf"
    c = canvas.Canvas(file)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT student_id, student_name, date, status FROM attendance")
    records = cur.fetchall()

    y = 800
    c.setFont("Helvetica", 10)

    for row in records:
        c.drawString(50, y, f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
        y -= 20

    conn.close()
    c.save()

    return send_file(file, as_attachment=True)
@app.route('/reports')
def reports():
    return render_template("report.html")
# ---------------- ATTENDANCE REPORT ----------------
@app.route('/attendance_report')
def attendance_report():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM attendance")
    records = cur.fetchall()

    conn.close()

    return render_template("attendance_report.html", records=records)


@app.route('/search', methods=['GET', 'POST'])
def search():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    students = []

    if request.method == 'POST':
        keyword = request.form['keyword']

        cur.execute("""
            SELECT * FROM students
            WHERE student_id LIKE ? OR name LIKE ?
        """, ('%' + keyword + '%', '%' + keyword + '%'))

        students = cur.fetchall()

    conn.close()

    return render_template("search.html", students=students)
# ---------------- ANALYTICS ----------------
@app.route('/analytics')
def analytics():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")
    total_students = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM attendance")
    total_attendance = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM activities")
    total_activities = cur.fetchone()[0]

    conn.close()

    return render_template(
        "analytics.html",
        total_students=total_students,
        total_attendance=total_attendance,
        total_activities=total_activities
    )
# ---------------- LOW ATTENDANCE REPORT ----------------
@app.route('/low_attendance')
def low_attendance():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT student_id, student_name, date, status
        FROM attendance
        WHERE status='Absent'
    """)

    records = cur.fetchall()

    conn.close()

    return render_template("low_attendance.html", records=records)
# ---------------- QR ATTENDANCE ----------------
@app.route('/qr_attendance')
def qr_attendance():
    return render_template("qr_attendance.html")

# ---------------- QR ATTENDANCE ----------------
@app.route('/generate_qr')
def generate_qr():
    attendance_url = "http://127.0.0.1:5000/attendance"

    img = qrcode.make(attendance_url)

    folder = os.path.join("static", "qr")

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = os.path.join(folder, "attendance_qr.png")

    print("Saving QR to:", filename)

    img.save(filename)

    print("QR Saved Successfully")

    return render_template(
        "qr_attendance.html",
        qr_image="qr/attendance_qr.png"
    )
# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)