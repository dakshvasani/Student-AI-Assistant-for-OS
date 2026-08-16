from pathlib import Path
from pypdf import PdfReader


PDF_FOLDER = Path("documents")


def read_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page_number, page in enumerate(reader.pages, start=1):

        page_text = page.extract_text()

        if page_text:
            text += f"\n\n--- Page {page_number} ---\n"
            text += page_text

    return text


def read_all_pdfs():

    all_text = ""

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found.")
        return ""

    for pdf_file in pdf_files:

        print(f"Reading: {pdf_file.name}")

        text = read_pdf(pdf_file)

        all_text += f"\n\n===== {pdf_file.name} =====\n"
        all_text += text

    return all_text


if __name__ == "__main__":

    extracted_text = read_all_pdfs()

    print("\nPDF reading completed.")
    print(f"Total characters extracted: {len(extracted_text)}")

    with open("extracted_text.txt", "w", encoding="utf-8") as file:
        file.write(extracted_text)

    print("Saved extracted text to extracted_text.txt")