from together import Together
from sentence_transformers import SentenceTransformer, util
from database import get_all_resumes_with_content, filter_by_experience
import streamlit as st
import json
import re


# Initialize Together.ai client
client = Together(api_key=st.secrets["TOGETHER_API_KEY"])

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')


# --------------------------
# ✅ General Chat
# --------------------------
def chat_with_bot(messages):
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Chatbot error: {e}")
        return "⚠️ Error responding. Please try again."


# --------------------------
# ✅ Smart Resume Search (with optional experience filter)
# --------------------------
def search_resumes(query, min_years_experience=0, top_k=5):
    try:
        if min_years_experience > 0:
            resumes = filter_by_experience(min_years_experience)
        else:
            resumes = get_all_resumes_with_content()

        if not resumes:
            return []

        file_names = [r[0] for r in resumes]
        urls = [r[1] for r in resumes]
        texts = [r[2] for r in resumes]

        resume_embeddings = embedder.encode(texts, convert_to_tensor=True)
        query_embedding = embedder.encode(query, convert_to_tensor=True)

        hits = util.cos_sim(query_embedding, resume_embeddings)[0]
        top_results = hits.topk(k=min(top_k, len(file_names)))

        results = []
        for score, idx in zip(top_results.values, top_results.indices):
            results.append({
                "file_name": file_names[idx],
                "url": urls[idx],
                "score": round(float(score), 2)
            })
        return results

    except Exception as e:
        st.error(f"Search error: {e}")
        return []


# --------------------------
# ✅ LLM-driven Experience Extraction
# --------------------------
def extract_experience_with_llm(resume_text):
    prompt = f"""
You are an expert recruiter.

Read the resume below and extract:
- years_of_experience: Total years of professional experience.

Return only JSON like:
{{"years_of_experience": 3}}

Resume Text:
{resume_text}
"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=300
        )

        content = resp.choices[0].message.content.strip()

        # Fallback in case JSON isn't perfectly formatted
        json_str = re.search(r"\{.*\}", content, re.DOTALL)
        if json_str:
            data = json.loads(json_str.group())
            years = int(data.get("years_of_experience", 0))
            return years if years >= 0 else 0
        else:
            return 0

    except Exception as e:
        st.warning(f"Experience extraction failed: {e}")
        return 0


# --------------------------
# ✅ LLM-driven Intent Detection
# --------------------------
def detect_intent(prompt):
    instruction = f"""
You are an AI recruiter assistant.

Check whether the following user message is:
1) resume_search — if the user is asking to find, filter, shortlist, screen, or search resumes/candidates/profiles.
2) general_chat — if the message is general conversation not related to searching resumes.

If intent is resume_search, also extract:
- min_years_experience: Minimum years of experience if mentioned (or 0 if not mentioned).

Return ONLY JSON like:
{{"intent": "resume_search", "min_years_experience": 2}}
OR
{{"intent": "general_chat"}}

User Message:
{prompt}
"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": instruction}],
            temperature=0.2,
            max_tokens=300
        )

        content = resp.choices[0].message.content.strip()

        json_str = re.search(r"\{.*\}", content, re.DOTALL)
        if json_str:
            data = json.loads(json_str.group())
            return data
        else:
            return {"intent": "general_chat"}

    except Exception as e:
        st.warning(f"Intent detection failed: {e}")
        return {"intent": "general_chat"}