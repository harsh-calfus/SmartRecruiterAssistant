from together import Together
import streamlit as st
import json
from database import filter_resumes

# Initialize Together.ai client (reads TOGETHER_API_KEY from secrets or env)
client = Together()

def general_chat(prompt: str) -> str:
    """
    Send a general user prompt to the LLM and return the assistant's reply.
    """
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def jd_based_resume_filter(jd_text: str) -> tuple[list[str], int]:
    """
    Extract skills & min years from a job description via the LLM,
    then filter resumes in the database accordingly.
    """
    system_msg = (
        "You are an AI recruiter assistant.  "
        "Read the following job description and extract:\n"
        "1) 'skills': a list of required skills\n"
        "2) 'min_experience_years': minimum years of experience\n\n"
        "Return ONLY a JSON object, for example:\n"
        "{\"skills\":[\"Python\",\"SQL\"],\"min_experience_years\":3}\n\n"
        "Job Description:\n" + jd_text
    )

    # Ask the model to produce the JSON
    resp = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "system",  "content": system_msg}
        ],
        temperature=0.2,
        max_tokens=200
    )

    content = resp.choices[0].message.content.strip()
    try:
        # Find the JSON substring and parse
        start = content.find("{")
        data = json.loads(content[start:])
        skills = data.get("skills", [])
        min_exp = data.get("min_experience_years", 0)
    except Exception:
        skills, min_exp = [], 0

    # Filter resumes in the database by these criteria
    return filter_resumes(skills, min_exp)
