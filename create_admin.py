from db import get_connection
from werkzeug.security import generate_password_hash

try:
    conn = get_connection()
    cursor = conn.cursor()
    hashed_pw = generate_password_hash('password123')
    cursor.execute('INSERT INTO admin (username, password) VALUES (%s, %s)', ('admin123', hashed_pw))
    conn.commit()
    print("--- SUCCESS: Admin 'admin123' created with password 'password123' ---")
except Exception as e:
    print(f"--- ERROR: {e} ---")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()
