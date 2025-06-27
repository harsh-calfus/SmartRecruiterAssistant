from huggingface_hub import InferenceClient
import streamlit as st
from database import filter_resumes


client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=st.secrets["HF_TOKEN"]
)


def general_chat(prompt):
    response = client.chat(
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_new_tokens=500,
        temperature=0.7
    )
    return response


def jd_based_resume_filter(jd_text):
    system_prompt = (
        "You are an AI recruiter assistant. Extract key skills and minimum years "
        "of experience from this job description. Return a JSON like this:\n\n"
        "{'skills': ['skill1', 'skill2'], 'min_experience_years': number}\n\n"
        "Job Description:\n"
    )

    combined = system_prompt + jd_text

    response = client.chat(
        messages=[
            {"role": "user", "content": combined}
        ],
        max_new_tokens=700,
        temperature=0.2
    )

    import json
    try:
        filters = json.loads(response)
        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)

        return filter_resumes(skills, min_exp)

    except Exception:
        return [{"error": "Failed to parse JD into filters."}]
