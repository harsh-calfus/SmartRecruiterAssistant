from huggingface_hub import InferenceClient
import streamlit as st


client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=st.secrets["HF_TOKEN"]
)


def general_chat(prompt):
    response = client.chat.completions(
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content


def jd_based_resume_filter(jd_text):
    system_prompt = (
        "You are an AI recruiter assistant. Extract key skills and minimum years "
        "of experience from this job description. Return a JSON like this:\n\n"
        "{'skills': ['skill1', 'skill2'], 'min_experience_years': number}\n\n"
        "Job Description:\n"
    )

    combined = system_prompt + jd_text

    response = client.chat.completions(
        messages=[
            {"role": "user", "content": combined}
        ],
        max_tokens=700,
        temperature=0.2
    )

    import json
    try:
        filters = json.loads(response.choices[0].message.content)
        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)

        return skills, min_exp

    except Exception:
        return [], 0
