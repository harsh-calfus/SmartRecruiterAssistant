import psycopg2
import streamlit as st


# Connect to PostgreSQL
conn = psycopg2.connect(st.secrets["DB_URL"])
cur = conn.cursor()


# ✅ Create Table
def create_table():
    try:
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
    except Exception as e:
        conn.rollback()
        st.error(f"Error creating table: {e}")


# ✅ Insert Resume with years_of_experience
def insert_resume(file_name, url, content, years_of_experience):
    try:
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
    except Exception as e:
        conn.rollback()
        st.error(f"Error inserting resume: {e}")


# ✅ Fetch All Resumes (for display)
def get_all_resumes():
    try:
        cur.execute("SELECT file_name, url FROM resumes")
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        st.error(f"Error fetching resumes: {e}")
        return []


# ✅ Fetch Resumes with Content (for search)
def get_all_resumes_with_content():
    try:
        cur.execute("SELECT file_name, url, content FROM resumes")
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        st.error(f"Error fetching resumes with content: {e}")
        return []


# ✅ Delete Resume
def delete_resume(file_name):
    try:
        cur.execute("DELETE FROM resumes WHERE file_name = %s", (file_name,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Error deleting resume: {e}")


# ✅ Filter by Minimum Experience (Optional)
def filter_by_experience(min_experience_years):
    try:
        cur.execute(
            """
            SELECT file_name, url, content FROM resumes
            WHERE years_of_experience >= %s
            """,
            (min_experience_years,),
        )
        return cur.fetchall()
    except Exception as e:
        conn.rollback()
        st.error(f"Error filtering resumes: {e}")
        return []