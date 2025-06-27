from huggingface_hub import InferenceClient
import streamlit as st
import json

# Initialize client without a default model
client = InferenceClient(token=st.secrets["HF_TOKEN"])

# Pick a free text-generation model that supports the free Inferencing API
TEXT_MODEL = "EleutherAI/gpt-neo-2.7B"

def general_chat(prompt: str) -> str:
    response = client.text_generation(
        model=TEXT_MODEL,
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.7,
    )
    return response.strip()

def jd_based_resume_filter(jd_text: str) -> tuple[list[str], int]:
    prompt = (
        "You are an AI recruiter assistant. Extract key skills and minimum years "
        "of experience from this job description and return ONLY valid JSON:\n"
        '{"skills": ["skill1","skill2"], "min_experience_years": number}\n\n'
        "Job Description:\n" + jd_text + "\n\nJSON:"
    )

    response = client.text_generation(
        model=TEXT_MODEL,
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.2,
    )

    try:
        # locate and parse JSON
        json_start = response.find("{")
        data = json.loads(response[json_start:])
        return data.get("skills", []), data.get("min_experience_years", 0)
    except Exception:
        return [], 0
