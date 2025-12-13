from db import get_connection

def admin_page(username):
    print("\n===== ADMIN PAGE =====")
    print(f"Welcome Admin: {username}")
    print("1. Add Teacher")
    print("2. View Reports")
    print("3. Logout")

def teacher_page(username):
    print("\n===== TEACHER PAGE =====")
    print(f"Welcome Teacher: {username}")
    print("1. Mark Attendance")
    print("2. View Attendance")
    print("3. Logout")

def login():
    print("===== LOGIN SYSTEM =====")
    role = input("Login as (admin/teacher): ").lower()
    username = input("Username: ")
    password = input("Password: ")

    conn = get_connection()
    cursor = conn.cursor()

    if role == "admin":
        query = "SELECT * FROM admin WHERE username=%s AND password=%s"
    elif role == "teacher":
        query = "SELECT * FROM teacher WHERE username=%s AND password=%s"
    else:
        print("Invalid role!")
        return

    cursor.execute(query, (username, password))
    result = cursor.fetchone()

    if result:
        print("\nLogin Successful!")
        if role == "admin":
            admin_page(username)
        else:
            teacher_page(username)
    else:
        print("\nLogin Failed! Invalid credentials.")

    cursor.close()
    conn.close()

login()
