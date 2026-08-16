from pathlib import Path
import json

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


UPLOAD_FOLDER = Path("uploads")
VECTOR_FILE = Path("vector_store.json")

CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

MODEL_NAME = "all-MiniLM-L6-v2"


# ------------------------------------------
# Load embedding model
# ------------------------------------------

model = SentenceTransformer(MODEL_NAME)


# ------------------------------------------
# Extract PDF text
# ------------------------------------------

def extract_pdf_text(pdf_path):

    reader = PdfReader(pdf_path)

    text = ""

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        page_text = page.extract_text()

        if page_text:

            text += (
                f"\n\n--- Page {page_number} ---\n"
            )

            text += page_text

    return text


# ------------------------------------------
# Create chunks
# ------------------------------------------

def create_chunks(text):

    chunks = []

    start = 0
    chunk_number = 1

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk_text = text[start:end].strip()

        if chunk_text:

            chunks.append({
                "chunk_id": chunk_number,
                "text": chunk_text
            })

            chunk_number += 1

        start = end - CHUNK_OVERLAP

    return chunks


# ------------------------------------------
# Create embeddings
# ------------------------------------------

def create_embeddings(chunks):

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    results = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        results.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": embedding.tolist()
        })

    return results


# ------------------------------------------
# Save vector store
# ------------------------------------------

def save_vector_store(vectors):

    with open(
        VECTOR_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            vectors,
            file,
            ensure_ascii=False
        )


# ------------------------------------------
# Process uploaded PDF
# ------------------------------------------

def process_pdf(pdf_path):

    print(
        f"Processing PDF: {pdf_path.name}"
    )

    # 1. Extract text
    text = extract_pdf_text(
        pdf_path
    )

    print(
        f"Extracted {len(text)} characters"
    )

    # 2. Create chunks
    chunks = create_chunks(text)

    print(
        f"Created {len(chunks)} chunks"
    )

    # 3. Create embeddings
    vectors = create_embeddings(
        chunks
    )

    print(
        f"Created {len(vectors)} embeddings"
    )

    # 4. Save
    save_vector_store(
        vectors
    )

    print(
        "Vector store updated successfully."
    )

    return {
        "filename": pdf_path.name,
        "characters": len(text),
        "chunks": len(chunks)
    }