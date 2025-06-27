import streamlit as st
from openai import OpenAI
from database import filter_resumes

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def general_chat(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def jd_based_resume_filter(jd_text):
    system_prompt = (
        "You are an AI recruiter assistant. Extract skills, years of experience, "
        "technologies, and relevant filters from the following job description. "
        "Return them as JSON with fields: skills, min_experience_years."
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": jd_text},
        ],
    )
    content = response.choices[0].message.content
    import json
    try:
        filters = json.loads(content)
        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)

        return filter_resumes(skills, min_exp)
    except:
        return [{"error": "Failed to parse JD into filters"}]
