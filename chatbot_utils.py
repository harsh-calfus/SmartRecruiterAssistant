from huggingface_hub import InferenceClient
import streamlit as st
import json

# Initialize client without default model
client = InferenceClient(token=st.secrets["HF_TOKEN"])

# Use flan-t5-base, which supports text_generation on free-tier
TEXT_MODEL = "google/flan-t5-base"

def general_chat(prompt: str) -> str:
    response = client.text_generation(
        model=TEXT_MODEL,
        prompt=prompt,
        max_new_tokens=150,
        temperature=0.7,
    )
    return response.strip()

def jd_based_resume_filter(jd_text: str) -> tuple[list[str], int]:
    prompt = (
        "Extract key skills and minimum years of experience from this job description "
        "and return ONLY valid JSON. Example:\n"
        '{"skills": ["Python", "SQL"], "min_experience_years": 3}\n\n'
        "Job Description:\n" + jd_text + "\n\nJSON:"
    )
    response = client.text_generation(
        model=TEXT_MODEL,
        prompt=prompt,
        max_new_tokens=150,
        temperature=0.2,
    )
    try:
        json_start = response.find("{")
        data = json.loads(response[json_start:])
        return data.get("skills", []), data.get("min_experience_years", 0)
    except Exception:
        return [], 0
