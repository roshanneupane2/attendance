import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Xavier@1234",
            database="attendancemanagementsystem",
            auth_plugin='mysql_native_password'  # Needed for Ubuntu/MySQL 8
        )
        return conn
    except Error as err:
        # Stop returning None, raise the error to see exact problem
        raise Error(f"MySQL connection failed: {err}")
