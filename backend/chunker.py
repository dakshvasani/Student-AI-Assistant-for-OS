from pathlib import Path
import json


INPUT_FILE = Path("extracted_text.txt")
OUTPUT_FILE = Path("chunks.json")

# Number of characters in each chunk
CHUNK_SIZE = 1500

# Overlap between chunks
CHUNK_OVERLAP = 200


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


def main():

    if not INPUT_FILE.exists():
        print("extracted_text.txt not found.")
        return

    print("Reading extracted text...")

    text = INPUT_FILE.read_text(
        encoding="utf-8"
    )

    print(f"Total characters: {len(text)}")

    chunks = create_chunks(text)

    print(f"Total chunks created: {len(chunks)}")

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            indent=2,
            ensure_ascii=False
        )

    print("Chunks saved to chunks.json")


if __name__ == "__main__":
    main()