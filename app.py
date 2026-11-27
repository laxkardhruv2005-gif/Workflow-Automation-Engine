
from flask import Flask, render_template_string, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


def connect_db():
    return sqlite3.connect("workflow.db")


def setup_database():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        email TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workflow_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_name TEXT,
        status TEXT,
        execution_time TEXT
    )
    """)

    conn.commit()
    conn.close()


HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Workflow Automation Engine</title>

<style>
body {
    font-family: Arial;
    background: #eef2f7;
    margin: 0;
    padding: 30px;
}

.container {
    max-width: 1000px;
    margin: auto;
}

.card {
    background: white;
    padding: 25px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 3px 12px #ccc;
}

h1 {
    color: #263b65;
}

.dashboard {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
}

.stat {
    flex: 1;
    min-width: 150px;
    background: #e8efff;
    padding: 20px;
    border-radius: 10px;
}

.stat h2 {
    color: #3157c8;
}

input {
    width: 95%;
    padding: 12px;
    margin: 8px 0;
    border: 1px solid #ccc;
    border-radius: 6px;
}

button {
    background: #3157c8;
    color: white;
    padding: 12px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

table {
    width: 100%;
    border-collapse: collapse;
}

td, th {
    padding: 12px;
    border-bottom: 1px solid #ddd;
    text-align: left;
}

.success {
    color: green;
}

.rejected {
    color: red;
}
</style>
</head>

<body>
<div class="container">

<h1>Workflow Automation Engine</h1>
<p>Automate repetitive tasks with Python and SQLite</p>

<div class="card">
<h2>Dashboard Overview</h2>

<div class="dashboard">

<div class="stat">
<h3>Total Students</h3>
<h2>{{ total_students }}</h2>
</div>

<div class="stat">
<h3>Successful Workflows</h3>
<h2>{{ successful }}</h2>
</div>

<div class="stat">
<h3>Rejected Workflows</h3>
<h2>{{ rejected }}</h2>
</div>

</div>
</div>

<div class="card">
<h2>Student Registration Workflow</h2>

<form method="POST" action="/register">

<input name="name" placeholder="Enter Student Name" required>

<input name="age" type="number" placeholder="Enter Age" min="1" required>

<input name="email" type="email" placeholder="Enter Email" required>

<button type="submit">Run Workflow</button>

</form>

{% if message %}
<h3 class="{{ status_class }}">{{ message }}</h3>
{% endif %}

</div>

<div class="card">
<h2>Registered Students</h2>

<table>
<tr>
<th>ID</th>
<th>Name</th>
<th>Age</th>
<th>Email</th>
</tr>

{% for student in students %}
<tr>
<td>{{ student[0] }}</td>
<td>{{ student[1] }}</td>
<td>{{ student[2] }}</td>
<td>{{ student[3] }}</td>
</tr>
{% endfor %}

</table>
</div>

<div class="card">
<h2>Workflow Execution History</h2>

<table>
<tr>
<th>Workflow</th>
<th>Status</th>
<th>Time</th>
</tr>

{% for log in logs %}
<tr>
<td>{{ log[0] }}</td>
<td>{{ log[1] }}</td>
<td>{{ log[2] }}</td>
</tr>
{% endfor %}

</table>
</div>

</div>
</body>
</html>
"""


@app.route("/")
def home():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    students = cursor.fetchall()

    cursor.execute("""
    SELECT workflow_name, status, execution_time
    FROM workflow_logs ORDER BY id DESC
    """)
    logs = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM workflow_logs
    WHERE status='Success'
    """)
    successful = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM workflow_logs
    WHERE status='Rejected'
    """)
    rejected = cursor.fetchone()[0]

    conn.close()

    return render_template_string(
        HTML,
        students=students,
        logs=logs,
        total_students=total_students,
        successful=successful,
        rejected=rejected,
        message=request.args.get("message"),
        status_class=request.args.get("status")
    )


@app.route("/register", methods=["POST"])
def register():

    name = request.form["name"].strip()
    age = int(request.form["age"])
    email = request.form["email"].strip()

    conn = connect_db()
    cursor = conn.cursor()

    if age >= 18:

        cursor.execute(
            "INSERT INTO students (name, age, email) VALUES (?, ?, ?)",
            (name, age, email)
        )

        status = "Success"
        message = "Registration Successful! Student saved."
        status_class = "success"

    else:

        status = "Rejected"
        message = "Registration Rejected! Age must be 18 or above."
        status_class = "rejected"

    cursor.execute("""
    INSERT INTO workflow_logs
    (workflow_name, status, execution_time)
    VALUES (?, ?, ?)
    """, (
        "Student Registration",
        status,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    return redirect(
        "/?message=" + message.replace(" ", "+")
        + "&status=" + status_class
    )


if __name__ == "__main__":
    setup_database()
    app.run(debug=True)