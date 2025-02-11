# database.py
import psycopg2
import streamlit as st

@st.cache_resource
def get_connection():
    """
    Returns a cached connection to PostgreSQL using credentials from st.secrets["postgres"].
    """
    conn = psycopg2.connect(
        host=st.secrets["postgres"]["host"],
        database=st.secrets["postgres"]["database"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        port=st.secrets["postgres"].get("port", 5432),
    )
    return conn

def init_db():
    """
    Creates 'reps' and 'demo_analysis' tables if they don't already exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Table: reps
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reps (
            id SERIAL PRIMARY KEY,
            rep_name TEXT UNIQUE NOT NULL,
            team TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # Table: demo_analysis
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS demo_analysis (
            id SERIAL PRIMARY KEY,
            rep_name TEXT NOT NULL,
            rep_team TEXT NOT NULL,
            customer_name TEXT,
            demo_date DATE,
            analysis_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    cur.close()
    #conn.close()


# ----------------------
# Reps Table Functions
# ----------------------
def fetch_all_reps():
    """
    Returns list of tuples (id, rep_name, team, created_at).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, rep_name, team, created_at FROM reps ORDER BY rep_name ASC")
    rows = cur.fetchall()
    cur.close()
    #conn.close()
    return rows

def insert_rep(rep_name, team):
    """
    Inserts a new rep into 'reps' table (ignores duplicates).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO reps (rep_name, team)
        VALUES (%s, %s)
        ON CONFLICT (rep_name) DO NOTHING
        """,
        (rep_name, team),
    )
    conn.commit()
    cur.close()
    #conn.close()

def delete_rep(rep_id):
    """
    Removes a rep by ID.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reps WHERE id = %s", (rep_id,))
    conn.commit()
    cur.close()
    #conn.close()

def get_rep_team(rep_name):
    """
    Returns the team (e.g. 'DME' or 'Ortho') for the given rep_name, or None if not found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT team FROM reps WHERE rep_name = %s", (rep_name,))
    row = cur.fetchone()
    cur.close()
    #conn.close()
    return row[0] if row else None


# -----------------------------
# Demo Analysis Table Functions
# -----------------------------
def insert_demo_result(rep_name, rep_team, customer_name, demo_date, analysis_json):
    """
    Insert a record into demo_analysis table.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO demo_analysis (rep_name, rep_team, customer_name, demo_date, analysis_json)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (rep_name, rep_team, customer_name, demo_date, analysis_json),
    )
    conn.commit()
    cur.close()
    #conn.close()

def fetch_all_results():
    """
    Returns rows: (id, rep_name, rep_team, customer_name, demo_date, analysis_json, created_at).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, rep_name, rep_team, customer_name, demo_date, analysis_json, created_at
        FROM demo_analysis
        ORDER BY id DESC
        """
    )
    rows = cur.fetchall()
    cur.close()
    #conn.close()
    return rows

def delete_analysis_record(analysis_id):
    """
    Delete a row from the demo_analysis table by ID.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM demo_analysis WHERE id = %s", (analysis_id,))
    conn.commit()
    cur.close()
    #conn.close()
