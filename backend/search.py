import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


VECTOR_FILE = Path("vector_store.json")

MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def load_vector_store():

    if not VECTOR_FILE.exists():
        raise FileNotFoundError(
            "vector_store.json not found. "
            "Run embeddings.py first."
        )

    with open(
        VECTOR_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def search_documents(
    question,
    top_k=5
):

    vector_store = load_vector_store()

    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    results = []

    for item in vector_store:

        chunk_embedding = np.array(
            item["embedding"]
        )

        similarity = np.dot(
            question_embedding,
            chunk_embedding
        )

        results.append({
            "chunk_id": item["chunk_id"],
            "text": item["text"],
            "score": float(similarity)
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:top_k]


if __name__ == "__main__":

    question = input(
        "Enter your question: "
    )

    results = search_documents(
        question
    )

    print("\nTop relevant sections:\n")

    for result in results:

        print("=" * 70)

        print(
            f"Chunk ID: {result['chunk_id']}"
        )

        print(
            f"Similarity: {result['score']:.4f}"
        )

        print()

        print(result["text"][:1000])

        print()