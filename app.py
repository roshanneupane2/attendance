from flask import Flask, render_template, request, redirect, url_for, flash
from db import get_connection

app = Flask(__name__)
app.secret_key = "secret123"

# Homepage
@app.route("/")
def index():
    return render_template("index.html")

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form["role"]
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        if role == "admin":
            query = "SELECT * FROM admin WHERE username=%s AND password=%s"
        elif role == "teacher":
            query = "SELECT * FROM teacher WHERE username=%s AND password=%s"
        else:
            flash("Invalid role!")
            return redirect(url_for("login"))

        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            if role == "admin":
                return redirect(url_for("admin_page", username=username))
            else:
                return redirect(url_for("teacher_page", username=username))
        else:
            flash("Login failed! Invalid credentials.")
            return redirect(url_for("login"))

    return render_template("login.html")

# Admin page
@app.route("/admin/<username>")
def admin_page(username):
    return render_template("admin.html", username=username)

# Teacher page
@app.route("/teacher/<username>")
def teacher_page(username):
    return render_template("teacher.html", username=username)

if __name__ == "__main__":
    app.run(debug=True)
