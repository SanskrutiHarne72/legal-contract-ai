import sqlite3
import pandas as pd
import os
os.makedirs("database", exist_ok=True)
DB_NAME = "database/contracts.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS contracts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        contract_type TEXT,
        created_date TEXT,
        contract TEXT
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