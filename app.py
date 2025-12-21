import math
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from functools import wraps
from db import get_connection

app = Flask(__name__)
app.secret_key = "xavier_attendance_secret_key"

# ==========================================
# HELPER: Haversine Distance Calculation
# ==========================================
def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in meters
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ==========================================
# AUTH DECORATOR
# ==========================================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash("Please log in first.")
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash("Unauthorized access!")
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =========================
# PUBLIC ROUTES
# =========================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor(dictionary=True, buffered=True)
            
            table = "admin" if role == "admin" else "teacher"
            cursor.execute(f"SELECT * FROM {table} WHERE username=%s", (username,))
            user = cursor.fetchone()
            
            cursor.close()
            # The password check happens here. By using pbkdf2:sha256 in setup, 
            # check_password_hash will now work correctly.
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                session['role'] = role
                return redirect(url_for('admin_page' if role == 'admin' else 'teacher_page'))
            else:
                flash("Invalid username or password.")
        except Exception as e:
            print(f"Login Error: {e}")
            flash("Database connection error.")
        finally:
            if conn and conn.is_connected():
                conn.close()
            
    return render_template("login.html")

# =========================
# ADMIN ROUTES
# =========================

@app.route("/admin")
@login_required(role='admin')
def admin_page():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, faculty FROM teacher")
    teachers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin.html", username=session['username'], teachers=teachers)

@app.route("/add_teacher", methods=["POST"])
@login_required(role='admin')
def add_teacher():
    data = request.get_json()
    username = data.get("username")
    # UPDATED: Explicitly using pbkdf2:sha256 for compatibility
    password = generate_password_hash(data.get("password"), method='pbkdf2:sha256')
    faculty = data.get("faculty")

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teacher (username, password, faculty) VALUES (%s,%s,%s)",
                       (username, password, faculty))
        conn.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Teacher added successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route("/teacher_attendance_report")
@login_required(role='admin')
def teacher_attendance_report():
    teacher = request.args.get("teacher")
    date_val = request.args.get("date")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT t.username, t.faculty, a.attendance_date, a.present FROM teacher t LEFT JOIN teacher_attendance a ON t.username = a.username"
    params = []
    
    if teacher or date_val:
        query += " WHERE "
        filters = []
        if teacher: 
            filters.append("t.username = %s")
            params.append(teacher)
        if date_val: 
            filters.append("a.attendance_date = %s")
            params.append(date_val)
        query += " AND ".join(filters)

    cursor.execute(query, tuple(params))
    records = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(records)

# =========================
# TEACHER ROUTES
# =========================

@app.route("/teacher")
@login_required(role='teacher')
def teacher_page():
    return render_template("teacher.html", username=session['username'])

@app.route("/mark_attendance", methods=["POST"])
@login_required(role='teacher')
def mark_attendance():
    data = request.get_json()
    try:
        lat = float(data.get("latitude"))
        lon = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid GPS data."})

    # CAMPUS COORDINATES: Mahendranagar
    CAMPUS_LAT = 28.9600
    CAMPUS_LON = 80.5900
    MAX_DISTANCE = 200 # meters

    dist = calculate_distance(lat, lon, CAMPUS_LAT, CAMPUS_LON)

    if dist > MAX_DISTANCE:
        return jsonify({"success": False, "message": f"Verification failed. You are {int(dist)}m away from campus."})

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        
        cursor.execute("SELECT id FROM teacher_attendance WHERE username=%s AND attendance_date=%s", (session['username'], today))
        if cursor.fetchone():
            return jsonify({"success": False, "message": "Attendance already marked for today."})

        cursor.execute("INSERT INTO teacher_attendance (username, attendance_date, present, latitude, longitude) VALUES (%s,%s,1,%s,%s)",
                       (session['username'], today, lat, lon))
        conn.commit()
        cursor.close()
        return jsonify({"success": True, "message": "Attendance verified and marked!"})
    except Exception as e:
        print(f"Attendance Error: {e}")
        return jsonify({"success": False, "message": "Server error recording attendance."})
    finally:
        if conn and conn.is_connected():
            conn.close()

# =========================
# LOGOUT & UTILS
# =========================

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)