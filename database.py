import psycopg2
import streamlit as st


# Connect to PostgreSQL
conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()


# Create Table
def create_table():
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes (
            file_name TEXT PRIMARY KEY,
            url TEXT,
            content TEXT,
            years_of_experience INT
        )
        """
    )
    conn.commit()


# Insert Resume with years_of_experience
def insert_resume(file_name, url, content, years_of_experience):
    cur.execute(
        """
        INSERT INTO resumes (file_name, url, content, years_of_experience)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (file_name) DO UPDATE
        SET url=EXCLUDED.url,
            content=EXCLUDED.content,
            years_of_experience=EXCLUDED.years_of_experience
        """,
        (file_name, url, content, years_of_experience),
    )
    conn.commit()


# Fetch All Resumes
def get_all_resumes():
    cur.execute("SELECT file_name, url, content FROM resumes")
    return cur.fetchall()


# Delete Resume
def delete_resume(file_name):
    cur.execute("DELETE FROM resumes WHERE file_name = %s", (file_name,))
    conn.commit()


# (Optional) Filter by Minimum Experience if needed
def filter_by_experience(min_experience_years):
    cur.execute(
        """
        SELECT file_name, url, content FROM resumes
        WHERE years_of_experience >= %s
        """,
        (min_experience_years,),
    )
    return cur.fetchall()