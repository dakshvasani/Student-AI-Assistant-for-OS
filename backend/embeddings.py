import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


CHUNKS_FILE = Path("chunks.json")
VECTOR_FILE = Path("vector_store.json")

MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks():
    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            "chunks.json not found. Run chunker.py first."
        )

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


def save_vectors(data):
    with open(
        VECTOR_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False
        )


def main():

    print("Loading chunks...")

    chunks = load_chunks()

    print(f"Loaded {len(chunks)} chunks.")

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Creating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    vector_store = []

    for chunk, embedding in zip(
        chunks,
        embeddings
    ):

        vector_store.append({
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "embedding": embedding.tolist()
        })

    save_vectors(vector_store)

    print()
    print("Embedding creation completed.")
    print(f"Total vectors: {len(vector_store)}")
    print(f"Saved to: {VECTOR_FILE}")


if __name__ == "__main__":
    main()