from together import Together
from sentence_transformers import SentenceTransformer, util
from database import get_all_resumes
import streamlit as st


# Initialize Together.ai client
client = Together()

# Initialize embedding model
embedder = SentenceTransformer('all-MiniLM-L6-v2')


# Smart Resume Search
def search_resumes(query, top_k=5):
    resumes = get_all_resumes()
    if not resumes:
        return []

    file_names = [r[0] for r in resumes]
    texts = [r[2] for r in resumes]

    resume_embeddings = embedder.encode(texts, convert_to_tensor=True)
    query_embedding = embedder.encode(query, convert_to_tensor=True)

    hits = util.cos_sim(query_embedding, resume_embeddings)[0]
    top_results = hits.topk(k=min(top_k, len(file_names)))

    results = []
    for score, idx in zip(top_results.values, top_results.indices):
        results.append({
            "file_name": file_names[idx],
            "url": resumes[idx][1],
            "score": round(float(score), 2)
        })
    return results


# General Chatbot
def chat_with_bot(messages):
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()
