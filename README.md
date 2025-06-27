# Smart Recruiter Assistant

A Streamlit-based app where recruiters can:
- Upload resumes (PDF/DOCX)
- Store files on Cloudinary
- Store parsed resume metadata in NeonDB PostgreSQL
- Search, view, delete resumes
- Use an AI-powered chatbot to query resumes

## Features
- Fully cloud-native
- Resume dashboard for upload, search, delete
- AI chatbot to filter candidates based on skills and experience
- Automatic database table creation (no manual setup needed)

## Deployment
- Deploy on Streamlit Cloud or locally
- Configure `.streamlit/secrets.toml` with your Cloudinary and NeonDB credentials

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```