import psycopg2
import streamlit as st


conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()


def create_table():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            file_name TEXT PRIMARY KEY,
            url TEXT,
            content TEXT
        )
        """
    )
    conn.commit()


def insert_resume(file_name, url, content):
    cur.execute(
        """
        INSERT INTO resumes (file_name, url, content)
        VALUES (%s, %s, %s)
        ON CONFLICT (file_name) DO NOTHING
        """,
        (file_name, url, content),
    )
    conn.commit()


def get_all_resumes():
    cur.execute("SELECT file_name, url FROM resumes")
    return cur.fetchall()


def delete_resume(file_name):
    cur.execute("DELETE FROM resumes WHERE file_name = %s", (file_name,))
    conn.commit()


def filter_resumes(skills, min_experience_years):
    if not skills:
        query = "SELECT file_name, url FROM resumes"
    else:
        query = """
            SELECT file_name, url FROM resumes
            WHERE (
        """ + " AND ".join([f"content ILIKE '%{skill}%'" for skill in skills]) + ")"
    cur.execute(query)
    rows = cur.fetchall()
    return [{"file_name": row[0], "url": row[1]} for row in rows]
