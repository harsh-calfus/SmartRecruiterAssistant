from together import Together
from database import filter_resumes_by_skills_and_experience
import streamlit as st
import json
import re


# ✅ Initialize LLM client
client = Together(api_key=st.secrets["TOGETHER_API_KEY"])


# ------------------------------------------
# ✅ General Chat
# ------------------------------------------
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


# ------------------------------------------
# ✅ Smart Resume Search (SQL + Skill Matching)
# ------------------------------------------
def search_resumes_sql_first(required_skills, min_years_experience=0):
    try:
        if not required_skills:
            return []

        # SQL filter to reduce load
        resumes = filter_resumes_by_skills_and_experience(required_skills, min_years_experience)

        if not resumes:
            return []

        results = []
        for file_name, url, content, years_of_experience in resumes:
            text_lower = content.lower()

            matched_skills = []
            for skill in required_skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    matched_skills.append(skill.lower())

            match_count = len(matched_skills)

            if match_count > 0:
                results.append({
                    "file_name": file_name,
                    "url": url,
                    "years_of_experience": years_of_experience,
                    "matched_skills": matched_skills,
                    "match_count": match_count
                })

        # Sort: Most skills matched → Higher YOE
        results = sorted(results, key=lambda x: (-x['match_count'], -x['years_of_experience']))

        return results

    except Exception as e:
        st.error(f"Search error: {e}")
        return []


# ------------------------------------------
# ✅ Extract Experience using LLM
# ------------------------------------------
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
        json_str = re.search(r"\{.*\}", content, re.DOTALL)

        if json_str:
            data = json.loads(json_str.group())
            years = int(data.get("years_of_experience", 0))
            return max(years, 0)
        else:
            return 0

    except Exception as e:
        st.warning(f"Experience extraction failed: {e}")
        return 0


# ------------------------------------------
# ✅ Intent Detection with Skills Extraction
# ------------------------------------------
def detect_intent(prompt):
    instruction = f"""
You are an AI recruiter assistant.

Check whether the following user message is:
1) resume_search — if the user is asking to find, filter, shortlist, screen, or search resumes/candidates/profiles.
2) general_chat — if the message is general conversation not related to searching resumes.

If intent is resume_search, also extract:
- min_years_experience: Minimum years of experience if mentioned (default to 0 if not mentioned).
- required_skills: A list of skills or technologies mentioned in the message.

Return ONLY JSON like:
{{
  "intent": "resume_search",
  "min_years_experience": 2,
  "required_skills": ["flutter", "python", "sql"]
}}
OR
{{
  "intent": "general_chat"
}}

User Message:
{prompt}
"""
    try:
        resp = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[{"role": "user", "content": instruction}],
            temperature=0.2,
            max_tokens=400
        )

        content = resp.choices[0].message.content.strip()
        json_str = re.search(r"\{.*\}", content, re.DOTALL)

        if json_str:
            data = json.loads(json_str.group())
            data.setdefault("min_years_experience", 0)
            data.setdefault("required_skills", [])
            return data
        else:
            return {"intent": "general_chat"}

    except Exception as e:
        st.warning(f"Intent detection failed: {e}")
        return {"intent": "general_chat"}