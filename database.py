"""
database.py
------------
Handles all SQLite database interactions for the Smart Healthcare
Analytics app: user accounts, patient records, and prediction history.
"""

import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = "healthcare.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all required tables if they don't already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'doctor',
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_username TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            phone TEXT,
            address TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            disease TEXT,
            input_data TEXT,
            result TEXT,
            probability REAL,
            risk_level TEXT,
            created_at TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------
# USER FUNCTIONS
# ---------------------------------------------------------------------
def create_user(username, password_hash, full_name, role="doctor"):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (username, password_hash, full_name, role, datetime.now().isoformat())
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def get_user(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, full_name, role FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "password_hash": row[2], "full_name": row[3], "role": row[4]}
    return None


# ---------------------------------------------------------------------
# PATIENT FUNCTIONS
# ---------------------------------------------------------------------
def add_patient(owner_username, name, age, gender, phone, address):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO patients (owner_username, name, age, gender, phone, address, created_at) VALUES (?,?,?,?,?,?,?)",
        (owner_username, name, age, gender, phone, address, datetime.now().isoformat())
    )
    conn.commit()
    patient_id = cur.lastrowid
    conn.close()
    return patient_id


def get_patients(owner_username):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM patients WHERE owner_username = ? ORDER BY created_at DESC",
        conn, params=(owner_username,)
    )
    conn.close()
    return df


def delete_patient(patient_id):
    conn = get_connection()
    conn.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
    conn.execute("DELETE FROM predictions WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()


def get_patient_by_id(patient_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    row = cur.fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------
# PREDICTION FUNCTIONS
# ---------------------------------------------------------------------
def save_prediction(patient_id, disease, input_data, result, probability, risk_level):
    conn = get_connection()
    conn.execute(
        """INSERT INTO predictions
           (patient_id, disease, input_data, result, probability, risk_level, created_at)
           VALUES (?,?,?,?,?,?,?)""",
        (patient_id, disease, str(input_data), result, probability, risk_level, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_predictions_for_patient(patient_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM predictions WHERE patient_id = ? ORDER BY created_at DESC",
        conn, params=(patient_id,)
    )
    conn.close()
    return df


def get_all_predictions(owner_username):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT pr.*, p.name as patient_name FROM predictions pr
           JOIN patients p ON pr.patient_id = p.id
           WHERE p.owner_username = ?
           ORDER BY pr.created_at DESC""",
        conn, params=(owner_username,)
    )
    conn.close()
    return df
