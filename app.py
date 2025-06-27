
import streamlit as st
from database import (
    create_table, get_all_resumes, insert_resume, delete_resume
)
from cloudinary_utils import upload_to_cloudinary, delete_from_cloudinary, fetch_pdf
from chatbot_utils import general_chat, jd_based_resume_filter
from io import BytesIO
from PyPDF2 import PdfReader

create_table()

st.set_page_config(layout="wide")
st.title("🧠 Smart Recruiter Assistant")

tab1, tab2 = st.tabs(["📄 Resume Dashboard", "🤖 Recruiter Chatbot"])

with tab1:
    st.subheader("📄 Resume Dashboard")

    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF only)", type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()

            cloud_url = upload_to_cloudinary(BytesIO(file_bytes), uploaded_file.name)

            pdf_reader = PdfReader(BytesIO(file_bytes))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""

            insert_resume(uploaded_file.name, cloud_url, text)

        st.success("Upload complete!")

    resumes = get_all_resumes()
    st.subheader("Uploaded Resumes")

    col1, col2 = st.columns([2, 3])

    with col1:
        for resume in resumes:
            file_name = resume[0]
            cloud_url = resume[1]

            st.markdown(f"**[{file_name}]({cloud_url})**", unsafe_allow_html=True)

            cols = st.columns([1, 1])
            with cols[0]:
                if st.button(f"🗑️ Delete {file_name}"):
                    delete_from_cloudinary(file_name)
                    delete_resume(file_name)
                    st.experimental_rerun()
    with col2:
        selected_file = st.selectbox(
            "Select a file to preview", [r[0] for r in resumes]
        )
        if selected_file:
            pdf_content = fetch_pdf(selected_file)
            if pdf_content:
                st.subheader("PDF Preview")
                st.download_button(
                    label="Download PDF",
                    data=pdf_content,
                    file_name=selected_file,
                    mime="application/pdf",
                )
                st.components.v1.html(
                    f'<iframe src="data:application/pdf;base64,{pdf_content}" width="700" height="1000"></iframe>',
                    height=1000,
                )

with tab2:
    st.subheader("🤖 Recruiter Chatbot")

    mode = st.radio(
        "Select Mode",
        ["General Chat", "Filter Resumes using JD"],
        horizontal=True,
    )

    user_input = st.text_area("Your Query:")

    if st.button("Submit") and user_input:
        if mode == "General Chat":
            st.markdown("### 🤖 Response")
            output = general_chat(user_input)
            st.success(output)

        else:
            st.markdown("### 🎯 Matching Resumes")
            output = jd_based_resume_filter(user_input)
            st.table(output)
