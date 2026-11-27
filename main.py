# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import sqlite3
from datetime import datetime

# Database connection
conn = sqlite3.connect("workflow.db")
cursor = conn.cursor()

# Create Students Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    email TEXT
)
""")

# Create Workflow Logs Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS workflow_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT,
    status TEXT,
    execution_time TEXT
)
""")

conn.commit()


# Workflow Engine
def run_workflow(name, age, email):

    print("\nWorkflow Started...")

    # Trigger
    print("Trigger: New Student Registration")

    # Condition
    if age >= 18:

        # Action
        cursor.execute(
            "INSERT INTO students (name, age, email) VALUES (?, ?, ?)",
            (name, age, email)
        )

        status = "Success"
        print("Condition Passed: Age is 18 or above")
        print("Action: Student saved in database")

    else:
        status = "Rejected"
        print("Condition Failed: Age must be 18 or above")

    # Save Execution History
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

    print("Workflow Status:", status)


# View Students
def view_students():

    cursor.execute("SELECT * FROM students")
    records = cursor.fetchall()

    print("\n--- Registered Students ---")

    for student in records:
        print(student)


# View Workflow History
def view_history():

    cursor.execute("SELECT * FROM workflow_logs")
    records = cursor.fetchall()

    print("\n--- Workflow History ---")

    for record in records:
        print(record)


# Main Menu
while True:

    print("\n===== WORKFLOW AUTOMATION ENGINE =====")
    print("1. Register Student")
    print("2. View Students")
    print("3. View Workflow History")
    print("4. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":

        name = input("Enter Student Name: ")
        age = int(input("Enter Student Age: "))
        email = input("Enter Student Email: ")

        run_workflow(name, age, email)

    elif choice == "2":
        view_students()

    elif choice == "3":
        view_history()

    elif choice == "4":
        print("Thank you!")
        break

    else:
        print("Invalid Choice!")

conn.close()

