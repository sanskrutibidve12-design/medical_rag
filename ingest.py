import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

# -----------------------------
# STEP 1: LOAD ALL PDFs
# -----------------------------

def load_pdfs(data_path="data"):
    documents = []

    for root, _, files in os.walk(data_path):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                print(f"Loading: {file_path}")
                loader = PyPDFLoader(file_path)
                documents.extend(loader.load())

    return documents


# -----------------------------
# STEP 2: CHUNK THE TEXT
# -----------------------------

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(documents)
    return chunks


# -----------------------------
# STEP 3: CREATE EMBEDDINGS
# -----------------------------

def create_embeddings():
    print("Loading embedding model...")

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embedding_model


# -----------------------------
# STEP 4: STORE IN FAISS
# -----------------------------

from db_connection import supabase

def insert_document(content, embedding):

    data = {
        "content": content,
        "embedding": embedding
    }

    supabase.table("documents").insert(data).execute()

# -----------------------------
# MAIN FUNCTION
# -----------------------------

if __name__ == "__main__":
    print("Starting ingestion process...\n")

    docs = load_pdfs("data")
    print(f"Total documents loaded: {len(docs)}\n")

    chunks = split_documents(docs)
    print(f"Total chunks created: {len(chunks)}\n")

    embeddings = create_embeddings()

    print("Creating embeddings and inserting into Supabase...\n")

    for chunk in chunks:
        text = chunk.page_content

        vector = embeddings.embed_query(text)

        insert_document(text, vector)

    print("\nIngestion completed successfully 🚀")