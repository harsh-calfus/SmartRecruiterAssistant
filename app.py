import streamlit as st
from database import (
    create_table, get_all_resumes, insert_resume, delete_resume
)
from cloudinary_utils import upload_to_cloudinary, delete_from_cloudinary
from chatbot_utils import (
    chat_with_bot, search_resumes_sql_first, detect_intent, extract_experience_with_llm
)
from io import BytesIO
from PyPDF2 import PdfReader


# Initialize DB
# create_table()

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

                cloud_url = upload_to_cloudinary(
                    BytesIO(file_bytes), uploaded_file.name
                )

                pdf_reader = PdfReader(BytesIO(file_bytes))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() or ""

                # Extract experience using LLM
                years_of_experience = extract_experience_with_llm(text)

                insert_resume(
                    uploaded_file.name,
                    cloud_url,
                    text,
                    years_of_experience
                )

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
# 🤖 Recruiter Chatbot (ChatGPT Style UI)
# ------------------------------------------
with tab2:
    st.subheader("🤖 Recruiter Chatbot")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat styling
    st.markdown(
        """
        <style>
        .user-message {
            background-color: #DCF8C6;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: right;
        }
        .assistant-message {
            background-color: #F1F0F0;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            text-align: left;
        }
        .message-text {
            font-size: 16px;
            line-height: 1.6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    chat_container = st.container()

    # Render chat history
    with chat_container:
        for msg in st.session_state.messages:
            role_class = "user-message" if msg["role"] == "user" else "assistant-message"
            st.markdown(
                f'<div class="{role_class}"><div class="message-text">{msg["content"]}</div></div>',
                unsafe_allow_html=True,
            )

    prompt = st.chat_input("Ask me anything...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with chat_container:
            st.markdown(
                f'<div class="user-message"><div class="message-text">{prompt}</div></div>',
                unsafe_allow_html=True,
            )

        # ---- Intent Detection ----
        intent_result = detect_intent(prompt)
        intent = intent_result.get("intent", "general_chat")
        min_exp = intent_result.get("min_years_experience", 0)
        required_skills = intent_result.get("required_skills", [])

        if intent == "resume_search":
            if required_skills:
                results = search_resumes_sql_first(required_skills, min_exp)

                if results:
                    response = "### 🔍 *Top Matching Resumes:* ###\n\n"
                    for res in results:
                        matched_skills_str = ", ".join(res['matched_skills'])
                        response += (
                            f"- 📄 [**{res['file_name']}**]({res['url']})  \n"
                            f"&nbsp;&nbsp;&nbsp;• 🏆 **Years of Experience:** {res['years_of_experience']}  \n"
                            f"&nbsp;&nbsp;&nbsp;• 🔧 **Skills Matched:** {matched_skills_str}\n\n"
                        )
                else:
                    response = "⚠️ No matching resumes found based on the provided skills and experience."

            else:
                response = "❗ Please mention skills or technologies to filter resumes effectively."

        else:
            # ---- General Chat ----
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            response = chat_with_bot(messages)

        st.session_state.messages.append({"role": "assistant", "content": response})

        with chat_container:
            st.markdown(
                f'<div class="assistant-message"><div class="message-text">{response}</div></div>',
                unsafe_allow_html=True,
            )