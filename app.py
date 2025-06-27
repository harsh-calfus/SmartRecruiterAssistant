import streamlit as st
from database import (
    create_table, get_all_resumes, insert_resume, delete_resume
)
from cloudinary_utils import upload_to_cloudinary, delete_from_cloudinary
from chatbot_utils import general_chat, jd_based_resume_filter
from io import BytesIO
from PyPDF2 import PdfReader


# Initialize DB
create_table()

st.set_page_config(page_title="Smart Recruiter Assistant", layout="wide")
st.title("🧠 Smart Recruiter Assistant")

# Tabs
tab1, tab2 = st.tabs(["📄 Resume Dashboard", "🤖 Recruiter Chatbot"])

# ------------------------------------------
# 📄 Resume Dashboard
# ------------------------------------------
with tab1:
    st.subheader("📄 Resume Dashboard")

    with st.expander("📤 Upload Resumes"):
        uploaded_files = st.file_uploader(
            "Upload PDFs", type=["pdf"], accept_multiple_files=True
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

            st.success("Upload completed!")

    st.subheader("📚 Uploaded Resumes")

    resumes = get_all_resumes()

    if resumes:
        for resume in resumes:
            file_name, url = resume
            cols = st.columns([5, 1])
            with cols[0]:
                st.markdown(
                    f"**[{file_name}]({url})**", unsafe_allow_html=True
                )
            with cols[1]:
                if st.button("🗑️", key=f"delete_{file_name}"):
                    delete_from_cloudinary(file_name)
                    delete_resume(file_name)
                    st.experimental_rerun()
    else:
        st.info("No resumes uploaded yet.")

# ------------------------------------------
# 🤖 Recruiter Chatbot
# ------------------------------------------
with tab2:
    st.subheader("🤖 Recruiter Chatbot")

    mode = st.radio(
        "Choose Mode",
        ["General Chat", "Filter Resumes by Job Description"],
        horizontal=True,
    )

    user_input = st.text_area("Enter your query or job description:")

    if st.button("Submit") and user_input.strip():
        if mode == "General Chat":
            st.markdown("### 🤖 Response")
            output = general_chat(user_input)
            st.success(output)

        else:
            st.markdown("### 🎯 Matching Resumes")
            results = jd_based_resume_filter(user_input)

            if results:
                for item in results:
                    st.markdown(
                        f"✅ **[{item['file_name']}]({item['url']})**",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No matching resumes found.")
