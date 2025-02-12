# database.py
import psycopg2
import streamlit as st

@st.cache_resource
def get_connection():
    """
    Returns a cached connection to PostgreSQL using secrets.
    Remove @st.cache_resource if you want a new connection per query.
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
    Creates teams, reps, and demo_analysis tables if needed.
    """
    conn = get_connection()
    cur = conn.cursor()

    # 1) Teams table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id SERIAL PRIMARY KEY,
            team_name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2) Reps table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reps (
            id SERIAL PRIMARY KEY,
            rep_name TEXT UNIQUE NOT NULL,
            team TEXT NOT NULL,  -- storing the string name from 'teams.team_name'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 3) Demo analyses
    cur.execute("""
        CREATE TABLE IF NOT EXISTS demo_analysis (
            id SERIAL PRIMARY KEY,
            rep_name TEXT NOT NULL,
            rep_team TEXT NOT NULL,
            customer_name TEXT,
            demo_date DATE,
            analysis_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    #conn.close()

# --------------------
# Teams Table Functions
# --------------------
def fetch_all_teams():
    """
    Returns [(id, team_name, created_at), ...]
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, team_name, created_at FROM teams ORDER BY team_name ASC")
    rows = cur.fetchall()
    cur.close()
    return rows

def insert_team(team_name):
    """
    Insert a new team by name. If it already exists, ignore.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO teams (team_name)
        VALUES (%s)
        ON CONFLICT (team_name) DO NOTHING
    """, (team_name,))
    conn.commit()
    cur.close()

def delete_team(team_id):
    """
    Delete a team by its numeric id.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM teams WHERE id = %s", (team_id,))
    conn.commit()
    cur.close()

# --------------------
# Reps Table Functions
# --------------------
def fetch_all_reps():
    """
    Returns [(id, rep_name, team, created_at), ...]
    'team' is just a string that matches one of the 'teams.team_name'
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, rep_name, team, created_at FROM reps ORDER BY rep_name ASC")
    rows = cur.fetchall()
    cur.close()
    return rows

def insert_rep(rep_name, team_name):
    """
    Insert a rep with the given name & team string
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO reps (rep_name, team)
        VALUES (%s, %s)
        ON CONFLICT (rep_name) DO NOTHING
    """, (rep_name, team_name))
    conn.commit()
    cur.close()

def delete_rep(rep_id):
    """
    Delete a rep by ID
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM reps WHERE id = %s", (rep_id,))
    conn.commit()
    cur.close()

def get_rep_team(rep_name):
    """
    Return the 'team' string for the rep, or None if not found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT team FROM reps WHERE rep_name = %s", (rep_name,))
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None

# --------------------
# Demo Analysis Table
# --------------------
def insert_demo_result(rep_name, rep_team, customer_name, demo_date, analysis_json):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO demo_analysis (rep_name, rep_team, customer_name, demo_date, analysis_json)
        VALUES (%s, %s, %s, %s, %s)
    """, (rep_name, rep_team, customer_name, demo_date, analysis_json))
    conn.commit()
    cur.close()

def fetch_all_results():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, rep_name, rep_team, customer_name, demo_date, analysis_json, created_at
        FROM demo_analysis
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    cur.close()
    return rows

def delete_analysis_record(analysis_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM demo_analysis WHERE id = %s", (analysis_id,))
    conn.commit()
    cur.close()
