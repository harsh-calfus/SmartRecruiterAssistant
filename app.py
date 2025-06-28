import streamlit as st
from database import (
    create_table, get_all_resumes, insert_resume, delete_resume
)
from cloudinary_utils import upload_to_cloudinary, delete_from_cloudinary
from chatbot_utils import chat_with_bot, search_resumes
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
                    st.rerun()
    else:
        st.info("No resumes uploaded yet.")

# ------------------------------------------
# 🤖 Recruiter Chatbot (Like ChatGPT)
# ------------------------------------------
with tab2:
    st.subheader("🤖 Recruiter Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Fixed chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Check if prompt is about resumes
        if any(word in prompt.lower() for word in ["resume", "candidate", "profile", "cv", "developer"]):
            results = search_resumes(prompt)
            if results:
                response = "### 🔍 Top matching resumes:\n"
                for res in results:
                    response += f"- [{res['file_name']}]({res['url']}) (Relevance: {res['score']})\n"
            else:
                response = "No matching resumes found."
        else:
            # General chat with bot
            messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            response = chat_with_bot(messages)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
