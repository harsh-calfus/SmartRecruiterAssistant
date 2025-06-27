from huggingface_hub import InferenceClient
import streamlit as st
import json

client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=st.secrets["HF_TOKEN"]
)

def general_chat(prompt):
    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def jd_based_resume_filter(jd_text):
    system_message = (
        "You are an AI recruiter assistant. Extract key skills and minimum years "
        "of experience from the following job description.\n\n"
        "Return the output strictly in JSON format like:\n"
        '{"skills": ["skill1", "skill2"], "min_experience_years": number}\n\n'
        "Job Description:\n" + jd_text + "\n\nJSON Output:"
    )

    response = client.chat_completion(
        messages=[{"role": "user", "content": system_message}],
        max_tokens=700,
        temperature=0.2
    )

    try:
        content = response.choices[0].message.content.strip()
        json_start = content.find("{")
        json_str = content[json_start:].strip()
        filters = json.loads(json_str)

        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)
        return skills, min_exp

    except Exception:
        return [], 0
