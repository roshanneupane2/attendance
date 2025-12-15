from flask import Flask, render_template, request, redirect, url_for, flash, session
from db import get_connection  # Make sure your db.py has get_connection() function

app = Flask(__name__)
app.secret_key = "secret123"  # Required for flash messages

# =========================
# Homepage
# =========================
@app.route("/")
def index():
    return render_template("index.html")

# =========================
# Login Page
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        if not role or not username or not password:
            flash("Please fill in all fields!")
            return redirect(url_for("login"))

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Determine which table to check based on role
        if role.lower() == "admin":
            query = "SELECT * FROM admin WHERE username=%s AND password=%s"
        elif role.lower() == "teacher":
            query = "SELECT * FROM teacher WHERE username=%s AND password=%s"
        else:
            flash("Invalid role selected!")
            cursor.close()
            conn.close()
            return redirect(url_for("login"))

        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            # Optional: store user in session
            session['username'] = username
            session['role'] = role.lower()

            if role.lower() == "admin":
                return redirect(url_for("admin_page", username=username))
            else:  # Teacher
                # Redirect specific teachers to separate pages
                if username.lower() == "teacher1":
                    return redirect(url_for("teacher1_page", username=username))
                elif username.lower() == "teacher2":
                    return redirect(url_for("teacher2_page", username=username))
                else:
                    return redirect(url_for("teacher_page", username=username))
        else:
            flash("Login failed! Invalid credentials.")
            return redirect(url_for("login"))

    # GET request
    return render_template("login.html")

# =========================
# Admin Dashboard
# =========================
@app.route("/admin/<username>")
def admin_page(username):
    return render_template("admin.html", username=username)

# =========================
# Default Teacher Dashboard
# =========================
@app.route("/teacher/<username>")
def teacher_page(username):
    return render_template("teacher.html", username=username)

# =========================
# Teacher 1 Dashboard
# =========================
@app.route("/teacher1/<username>")
def teacher1_page(username):
    return render_template("teacher1.html", username=username)

# =========================
# Teacher 2 Dashboard
# =========================
@app.route("/teacher2/<username>")
def teacher2_page(username):
    return render_template("teacher2.html", username=username)

# =========================
# Logout (optional)
# =========================
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))

# =========================
# Run the App
# =========================
if __name__ == "__main__":
    app.run(debug=True)
