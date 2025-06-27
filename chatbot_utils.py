from huggingface_hub import InferenceClient
import streamlit as st
import json


client = InferenceClient(
    "mistralai/Mistral-7B-Instruct-v0.2",
    token=st.secrets["HF_TOKEN"]
)


def general_chat(prompt):
    system_prompt = (
        "You are a helpful AI assistant. Answer the following user query conversationally.\n\n"
        f"User: {prompt}\nAI:"
    )

    response = client.text_generation(
        prompt=system_prompt,
        max_new_tokens=500,
        temperature=0.7,
        repetition_penalty=1.2,
    )

    return response.strip()


def jd_based_resume_filter(jd_text):
    system_prompt = (
        "You are an AI recruiter assistant. Extract key skills and minimum years "
        "of experience from the following job description.\n\n"
        "Return the output strictly in JSON format like:\n"
        "{\"skills\": [\"skill1\", \"skill2\"], \"min_experience_years\": number}\n\n"
        "Job Description:\n"
        + jd_text
        + "\n\nJSON Output:"
    )

    response = client.text_generation(
        prompt=system_prompt,
        max_new_tokens=700,
        temperature=0.2,
        repetition_penalty=1.1,
    )

    try:
        # Clean and parse response
        json_start = response.find("{")
        json_str = response[json_start:].strip()
        filters = json.loads(json_str)

        skills = filters.get("skills", [])
        min_exp = filters.get("min_experience_years", 0)

        return skills, min_exp

    except Exception:
        return [], 0
