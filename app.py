import streamlit as st
from cloudinary_utils import upload_to_cloudinary, delete_from_cloudinary
from database import create_table_if_not_exists, insert_resume, fetch_resumes, delete_resume
from parser_utils import extract_text_from_pdf, extract_text_from_docx, parse_resume_text
from chatbot_utils import process_prompt
import pandas as pd
import io

st.set_page_config(page_title="Smart Recruiter Assistant", layout="wide")

# Create DB table if not exists
create_table_if_not_exists()

tab1, tab2 = st.tabs(["📄 Resume Dashboard", "🤖 Recruiter Chatbot"])

with tab1:
    st.header("📄 Resume Dashboard")
    uploaded_files = st.file_uploader("Upload Resumes", type=['pdf', 'docx'], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_bytes = uploaded_file.getvalue()

            cloud_url = upload_to_cloudinary(io.BytesIO(file_bytes), file_name)

            if file_name.endswith(".pdf"):
                text = extract_text_from_pdf(io.BytesIO(file_bytes))
            else:
                text = extract_text_from_docx(io.BytesIO(file_bytes))

            parsed = parse_resume_text(text)

            data = {
                "file_name": file_name,
                "cloudinary_url": cloud_url,
                "candidate_name": file_name.split('.')[0],
                "email": parsed["email"],
                "phone": parsed["phone"],
                "skills": parsed["skills"],
                "experience": parsed["experience"],
                "full_text": text
            }
            insert_resume(data)
            st.success(f"Uploaded {file_name}")

    st.subheader("📜 Resumes")
    df = fetch_resumes()
    st.dataframe(df)

    col1, col2 = st.columns([2, 1])
    with col1:
        delete_file = st.text_input("Enter file name to delete")
    with col2:
        if st.button("Delete"):
            delete_from_cloudinary(delete_file)
            delete_resume(delete_file)
            st.success(f"Deleted {delete_file}")

with tab2:
    st.header("🤖 Recruiter Chatbot")
    prompt = st.text_input("Ask me something...")

    if st.button("Send"):
        if "joke" in prompt.lower():
            st.info("Why do programmers prefer dark mode? Because light attracts bugs!")
        else:
            skills, exp = process_prompt(prompt)
            filter_query = "WHERE TRUE"
            if skills:
                skill_conditions = " OR ".join([f"'{skill}' = ANY(skills)" for skill in skills])
                filter_query += f" AND ({skill_conditions})"
            if exp > 0:
                filter_query += f" AND experience >= {exp}"

            result_df = fetch_resumes(filter_query)
            if result_df.empty:
                st.warning("No matching resumes found.")
            else:
                st.success(f"Found {len(result_df)} matching resumes")
                st.dataframe(result_df)