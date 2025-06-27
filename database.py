from sqlalchemy import create_engine, text
import pandas as pd
import streamlit as st

db_url = st.secrets["DATABASE_URL"]
engine = create_engine(db_url)

def create_table_if_not_exists():
    create_query = '''
    CREATE TABLE IF NOT EXISTS resumes (
        id SERIAL PRIMARY KEY,
        file_name TEXT UNIQUE,
        cloudinary_url TEXT,
        candidate_name TEXT,
        email TEXT,
        phone TEXT,
        skills TEXT[],
        experience INTEGER,
        full_text TEXT,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''
    with engine.connect() as conn:
        conn.execute(text(create_query))
        conn.commit()

def insert_resume(data):
    query = '''
    INSERT INTO resumes (file_name, cloudinary_url, candidate_name, email, phone, skills, experience, full_text)
    VALUES (:file_name, :cloudinary_url, :candidate_name, :email, :phone, :skills, :experience, :full_text)
    ON CONFLICT (file_name) DO NOTHING;
    '''
    with engine.connect() as conn:
        conn.execute(text(query), data)
        conn.commit()

def fetch_resumes(filters=""):
    query = f"SELECT * FROM resumes {filters}"
    df = pd.read_sql(query, engine)
    return df

def delete_resume(file_name):
    query = "DELETE FROM resumes WHERE file_name = :file_name"
    with engine.connect() as conn:
        conn.execute(text(query), {"file_name": file_name})
        conn.commit()