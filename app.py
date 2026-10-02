from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "student_management_secret_key"


# ---------------- DATABASE ----------------

def create_database():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            course TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect("/home")

        else:
            return render_template(
                "login.html",
                error="Invalid Username or Password"
            )

    return render_template("login.html")


# ---------------- DASHBOARD / HOME ----------------

@app.route("/home")
def home():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        total_students=total_students
    )


# ---------------- ADD STUDENT ----------------

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if "logged_in" not in session:
        return redirect("/")

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, roll_no, course, email)
            VALUES (?, ?, ?, ?)
        """, (name, roll_no, course, email))

        conn.commit()
        conn.close()

        return redirect("/view_students")

    return render_template("add_student.html")


# ---------------- VIEW STUDENTS ----------------

@app.route("/view_students")
def view_students():

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template(
        "view_students.html",
        students=students
    )


# ---------------- SEARCH STUDENT ----------------

@app.route("/search_student", methods=["GET", "POST"])
def search_student():

    if "logged_in" not in session:
        return redirect("/")

    students = []

    if request.method == "POST":

        search = request.form["search"]

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM students
            WHERE name LIKE ?
            OR roll_no LIKE ?
        """, (
            "%" + search + "%",
            "%" + search + "%"
        ))

        students = cursor.fetchall()

        conn.close()

    return render_template(
        "search_student.html",
        students=students
    )


# ---------------- EDIT STUDENT ----------------

@app.route("/edit_student/<int:id>", methods=["GET", "POST"])
def edit_student(id):

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        roll_no = request.form["roll_no"]
        course = request.form["course"]
        email = request.form["email"]

        cursor.execute("""
            UPDATE students
            SET name = ?,
                roll_no = ?,
                course = ?,
                email = ?
            WHERE id = ?
        """, (
            name,
            roll_no,
            course,
            email,
            id
        ))

        conn.commit()
        conn.close()

        return redirect("/view_students")

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit_student.html",
        student=student
    )


# ---------------- DELETE STUDENT ----------------

@app.route("/delete_student/<int:id>")
def delete_student(id):

    if "logged_in" not in session:
        return redirect("/")

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/view_students")


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- RUN APPLICATION ----------------

if __name__ == "__main__":

    create_database()

    app.run(debug=True)