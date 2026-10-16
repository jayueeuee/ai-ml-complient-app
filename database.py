import mysql.connector
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()
def get_db_connection():

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.getenv("MYSQL_PASSWORD", ""),
            database="grievance_db"
        )
        return conn

    except mysql.connector.Error as err:

        # If database doesn't exist, connect without database
        if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:

            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password=os.getenv("MYSQL_PASSWORD", "")
            )

            return conn

        else:
            raise err

def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create DB if it does no  t exist
    db_name = os.getenv("MYSQL_DATABASE", "grievance_db")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    cursor.execute(f"USE {db_name}")
    
    # Users Table (for User, Admin, Officer)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        email VARCHAR(255),
        phone VARCHAR(50),
        address TEXT
    )
    """)
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255)")
        cursor.execute("ALTER TABLE users ADD COLUMN phone VARCHAR(50)")
        cursor.execute("ALTER TABLE users ADD COLUMN address TEXT")
    except Exception:
        pass
    
    # Wards Table (for Sevak)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wards (
        id INT AUTO_INCREMENT PRIMARY KEY,
        ward_name VARCHAR(255) NOT NULL UNIQUE,
        nagar_sevak_name VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        username VARCHAR(255),
        password VARCHAR(255)
    )
    """)
    
    # Complaints Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id VARCHAR(50) PRIMARY KEY,
        description TEXT NOT NULL,
        lat FLOAT,
        lon FLOAT,
        ward VARCHAR(255),
        image_path VARCHAR(500),
        verification_status VARCHAR(50),
        category VARCHAR(100),
        priority VARCHAR(50),
        status VARCHAR(50) DEFAULT 'Pending',
        submission_date DATETIME,
        escalated BOOLEAN DEFAULT FALSE,
        resolution_proof VARCHAR(500),
        sevak_comments TEXT,
        user_name VARCHAR(255),
        user_contact VARCHAR(255),
        image_analysis TEXT
    )
    """)
    # try:
    #     cursor.execute("ALTER TABLE complaints ADD COLUMN user_name VARCHAR(255)")
    #     cursor.execute("ALTER TABLE complaints ADD COLUMN user_contact VARCHAR(255)")
    # except Exception:
    #     pass
    # try:
    #     cursor.execute("ALTER TABLE complaints ADD COLUMN image_analysis TEXT")
    # except Exception:
    #     pass
    
    # Feedback Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INT AUTO_INCREMENT PRIMARY KEY,
        complaint_id VARCHAR(50),
        rating INT,
        comment TEXT,
        submitted_at DATETIME,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id)
    )
    """)
    
    # Seed Wards if empty
    cursor.execute("SELECT COUNT(*) FROM wards")
    if cursor.fetchone()[0] == 0:
        wards_data = [
            ('Ward 1', 'Ramesh Patil', 'ward1@example.com', 'ward1', 'pass1'),
            ('Ward 2', 'Sunita Deshmukh', 'ward2@example.com', 'ward2', 'pass2'),
            ('Ward 3', 'Vikram Joshi', 'ward3@example.com', 'ward3', 'pass3'),
            ('Ward 4', 'Pooja Kadam', 'ward4@example.com', 'ward4', 'pass4')
        ]
        cursor.executemany("INSERT INTO wards (ward_name, nagar_sevak_name, email, username, password) VALUES (%s, %s, %s, %s, %s)", wards_data)
        
    # Seed default Admin
    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE role='Admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (name, username, password, role) VALUES ('System Admin', 'admin', 'admin123', 'Admin')")
    except Exception:
        pass
        
    conn.commit()
    cursor.close()
    conn.close()

def insert_complaint(complaint_id, desc, lat, lon, ward, img_path, v_status, category, priority, user_name, user_contact, image_analysis=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO complaints (id, description, lat, lon, ward, image_path, verification_status, category, priority, submission_date, user_name, user_contact, image_analysis)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (complaint_id, desc, lat, lon, ward, img_path, v_status, category, priority, datetime.now(), user_name, user_contact, image_analysis))
    conn.commit()
    cursor.close()
    conn.close()

def get_complaints_df():
    conn = get_db_connection()
    query = "SELECT * FROM complaints"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_complaints_by_user(user_name="", user_contact=""):
    """Fetch complaints matching user name or contact."""
    conn = get_db_connection()
    query = "SELECT * FROM complaints WHERE user_name = %s OR user_contact = %s ORDER BY submission_date DESC"
    df = pd.read_sql(query, conn, params=(user_name, user_contact))
    conn.close()
    return df

def get_wards_df():
    conn = get_db_connection()
    query = "SELECT * FROM wards"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def update_complaint_status(complaint_id, status, comments="", proof=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE complaints SET status=%s, sevak_comments=%s, resolution_proof=%s WHERE id=%s"
    cursor.execute(query, (status, comments, proof, complaint_id))
    conn.commit()
    cursor.close()
    conn.close()

def escalate_black_zone_complaints(days_threshold=3):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Mark complaints as escalated if Pending for more than threshold days
    # Using simple date math for MySQL
    query = f"""
    UPDATE complaints 
    SET escalated = TRUE, status = 'Black Zone' 
    WHERE status = 'Pending' AND DATEDIFF(NOW(), submission_date) >= %s
    """
    cursor.execute(query, (days_threshold,))
    updated_rows = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()
    return updated_rows

def add_ward(ward_name, sevak_name, email, username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO wards (ward_name, nagar_sevak_name, email, username, password)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (ward_name, sevak_name, email, username, password))
    conn.commit()
    cursor.close()
    conn.close()

def insert_feedback(complaint_id, rating, comment=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO feedback (complaint_id, rating, comment, submitted_at)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (complaint_id, rating, comment, datetime.now()))
    conn.commit()
    cursor.close()
    conn.close()

def get_feedback_df():
    conn = get_db_connection()
    query = "SELECT * FROM feedback"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_complaint_by_id(complaint_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM complaints WHERE id = %s"
    cursor.execute(query, (complaint_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def register_user(name, username, password, email, phone, address, role="User"):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO users (name, username, password, role, email, phone, address) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (name, username, password, role, email, phone, address))
        conn.commit()
        success = True
    except mysql.connector.IntegrityError:
        success = False # Username exists
    cursor.close()
    conn.close()
    return success

def authenticate_user(username, password, role):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE username = %s AND password = %s AND role = %s"
    cursor.execute(query, (username, password, role))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def authenticate_sevak(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM wards WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def reset_password(username, new_password, is_sevak=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    table = "wards" if is_sevak else "users"
    try:
        query = f"UPDATE {table} SET password = %s WHERE username = %s"
        cursor.execute(query, (new_password, username))
        conn.commit()
        success = cursor.rowcount > 0
    except Exception:
        success = False
    cursor.close()
    conn.close()
    return success
