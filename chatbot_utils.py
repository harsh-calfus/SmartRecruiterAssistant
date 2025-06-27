from huggingface_hub import InferenceClient
import streamlit as st
import json

# Use a free, text-generation–compatible model
client = InferenceClient(
    model="google/flan-t5-large",
    token=st.secrets["HF_TOKEN"]
)

def general_chat(prompt):
    # flan-t5-large expects a simple prompt string
    response = client.text_generation(
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.7
    )
    # response is a plain string
    return response.strip()

def jd_based_resume_filter(jd_text):
    # Prepend instructions to the JD
    prompt = (
        "Extract key skills and minimum years of experience from this job description.\n\n"
        "Return ONLY a JSON object, e.g.:\n"
        '{"skills": ["Python", "SQL"], "min_experience_years": 3}\n\n'
        "Job Description:\n"
        + jd_text
    )

    response = client.text_generation(
        prompt=prompt,
        max_new_tokens=200,
        temperature=0.2
    )

    try:
        # Find the first JSON object in the response
        json_start = response.find("{")
        json_str = response[json_start:]
        filters = json.loads(json_str)

        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)
        return skills, min_exp
    except Exception:
        return [], 0
