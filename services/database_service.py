import sqlite3
import pandas as pd
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "database", "contracts.db")
os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Original contracts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        contract_type TEXT,
        created_date TEXT,
        contract TEXT
    )
    """)

    # New unified history table for all module activities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contract_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_name TEXT,
        contract_type TEXT,
        activity_type TEXT,
        description TEXT,
        created_at TEXT,
        status TEXT DEFAULT 'Completed',
        result_content TEXT,
        file_path TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_contract(title, contract_type, created_date, contract):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO contracts(title,contract_type,created_date,contract)
    VALUES(?,?,?,?)
    """, (title, contract_type, created_date, contract))

    conn.commit()
    conn.close()


def get_contracts():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM contracts
    ORDER BY id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


def delete_contract(contract_id):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM contracts WHERE id=?",
        (contract_id,)
    )

    conn.commit()
    conn.close()
def get_total_contracts():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM contracts")

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_recent_contracts(limit=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, contract_type, created_date
        FROM contracts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    data = cursor.fetchall()

    conn.close()

    return data
def get_contract_type_data():
    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT contract_type,
           COUNT(*) AS total
    FROM contracts
    GROUP BY contract_type
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


def get_contract_date_data():
    conn = sqlite3.connect(DB_NAME)

    query = """
    SELECT created_date
    FROM contracts
    ORDER BY created_date
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df


# ============================================================
# CONTRACT HISTORY FUNCTIONS (Module 5)
# ============================================================

def save_history_record(contract_name, contract_type, activity_type,
                        description="", result_content="", file_path="", status="Completed"):
    """Save a new activity record to contract_history table."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO contract_history
              (contract_name, contract_type, activity_type, description, created_at, status, result_content, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (contract_name, contract_type, activity_type, description,
              created_at, status, result_content, file_path))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] save_history_record: {e}")
        return False


def get_history(search="", activity_filter="All", type_filter="All",
                status_filter="All", sort_order="Newest First"):
    """Fetch history records with optional search, filter, and sort."""
    try:
        conn = sqlite3.connect(DB_NAME)
        query = "SELECT id, contract_name, contract_type, activity_type, description, created_at, status FROM contract_history WHERE 1=1"
        params = []

        if search:
            query += " AND (contract_name LIKE ? OR contract_type LIKE ? OR activity_type LIKE ?)"
            s = f"%{search}%"
            params.extend([s, s, s])
        if activity_filter != "All":
            query += " AND activity_type = ?"
            params.append(activity_filter)
        if type_filter != "All":
            query += " AND contract_type LIKE ?"
            params.append(f"%{type_filter}%")
        if status_filter != "All":
            query += " AND status = ?"
            params.append(status_filter)

        query += " ORDER BY id " + ("DESC" if sort_order == "Newest First" else "ASC")

        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB ERROR] get_history: {e}")
        return []


def get_history_record(record_id):
    """Fetch a single full history record including result_content."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contract_history WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    except Exception as e:
        print(f"[DB ERROR] get_history_record: {e}")
        return None


def delete_history_record(record_id):
    """Delete a single history record."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contract_history WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB ERROR] delete_history_record: {e}")
        return False


def get_history_stats():
    """Return counts per activity_type for dashboard metrics."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT activity_type, COUNT(*) FROM contract_history
            WHERE status = 'Completed'
            GROUP BY activity_type
        """)
        rows = cursor.fetchall()
        conn.close()
        stats = {"Drafted": 0, "Reviewed": 0, "Clause Explained": 0, "Risk Analyzed": 0}
        for activity, count in rows:
            if activity in stats:
                stats[activity] = count
        stats["Total"] = sum(stats.values())
        return stats
    except Exception as e:
        print(f"[DB ERROR] get_history_stats: {e}")
        return {"Total": 0, "Drafted": 0, "Reviewed": 0, "Clause Explained": 0, "Risk Analyzed": 0}


def get_recent_history(limit=5):
    """Fetch the most recent N history records for the dashboard."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT contract_name, contract_type, activity_type, created_at, status
            FROM contract_history
            ORDER BY id DESC LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB ERROR] get_recent_history: {e}")
        return []