

import requests
from sentence_transformers import SentenceTransformer
from db_connection import supabase
import os

# --------------------------------
# Load embedding model
# --------------------------------
print("Loading embedding model...")
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# --------------------------------
# LM Studio API
# --------------------------------



GROQ_API_KEY = os.getenv("GROQ_API_KEY")
print("GROQ API Key loaded:", bool(GROQ_API_KEY))
# --------------------------------
# Search similar documents
# --------------------------------
def search_documents(query_embedding):
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": 5
        }
    ).execute()
    return response.data


# --------------------------------
# Ask LM Studio
# --------------------------------
def ask_llm(context, question):
    prompt = f"""
You are an expert Medical Research Assistant. Your goal is to provide accurate, 
clear, and empathetic information based on the provided clinical documentation.

### INSTRUCTIONS:
1. **Contextual Accuracy:** Use the provided context to answer the user's question. 
2. **Missing Information:** If the answer is not contained within the context, do not make up facts. Instead, politely explain that the provided documents do not cover that specific topic and suggest what information might be missing.
3. **Synthesis:** If the user mentions symptoms (like drowsiness), check the context for warning signs or complications.
4. **Tone:** Maintain a professional, supportive, and clinical tone.

### CONTEXT:
{context}

### USER QUERY:
{question}

### ASSISTANT RESPONSE:
"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
       "model": "llama-3.3-70b-versatile",  # fast + good
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )

    result = response.json()
    print(result)
    if "choices" in result:
      return result["choices"][0]["message"]["content"]
    else:
       return f"API Error: {result}"


# --------------------------------
# Check semantic cache
# --------------------------------
def check_similar_question(query_embedding):
    response = supabase.rpc(
        "match_conversations",
        {
            "query_embedding": query_embedding,
            "match_threshold": 0.90,
            "match_count": 1
        }
    ).execute()
    return response.data


# --------------------------------
# Store new conversation (only called on thumbs up)
# --------------------------------
def store_conversation(question, answer, embedding):
    supabase.table("conversations").insert({
        "question": question,
        "answer": answer,
        "embedding": embedding,
        "feedback": 1
    }).execute()


# --------------------------------
# Replace existing answer in DB (called on regenerate if question exists)
# --------------------------------
def replace_conversation(question, new_answer):
    supabase.table("conversations") \
        .update({"answer": new_answer, "feedback": None}) \
        .eq("question", question) \
        .execute()


# --------------------------------
# Check if question already exists exactly in DB
# --------------------------------
def get_existing_conversation(question):
    response = supabase.table("conversations") \
        .select("*") \
        .eq("question", question) \
        .execute()
    return response.data


# --------------------------------
# Update feedback
# --------------------------------
def update_feedback(question, feedback):
    supabase.table("conversations") \
        .update({"feedback": feedback}) \
        .eq("question", question) \
        .execute()


# --------------------------------
# Full RAG pipeline
# force_regenerate=True → skip cache, always call LLM
# auto_store=False → don't store in DB, wait for thumbs up
# --------------------------------
def chat(question, force_regenerate=False):

    print("Creating embedding...")
    query_embedding = embedding_model.encode(question).tolist()

    # Step 1: Check cache (skip if force_regenerate)
    if not force_regenerate:
        similar = check_similar_question(query_embedding)
        if similar:
            print("Answer retrieved from semantic cache")
            return similar[0]["answer"], query_embedding, True  # True = came from cache

    # Step 2: Run RAG pipeline
    print("Searching documents...")
    docs = search_documents(query_embedding)

    if not docs:
        return "I couldn't find relevant information in the documents.", query_embedding, False

    context = "\n".join([doc["content"] for doc in docs])

    print("Generating answer from LLM...")
    answer = ask_llm(context, question)

    return answer, query_embedding, False  # False = freshly generated


# --------------------------------
# Custom document upload pipeline
# Chunks, embeds and stores a user-uploaded document
# --------------------------------
def process_custom_document(text, source_name="custom_upload", chunk_size=400):
    """
    Takes raw text from an uploaded file, splits into chunks,
    embeds each chunk and stores in Supabase documents table.
    Returns number of chunks stored.
    """
    # Split text into chunks
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)

    stored = 0
    for i, chunk in enumerate(chunks):
        embedding = embedding_model.encode(chunk).tolist()
        supabase.table("documents").insert({
            "content": chunk,
            "embedding": embedding,
            "source": f"{source_name}_chunk_{i+1}"
        }).execute()
        stored += 1

    return stored