import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from search import search_documents
from document_processor import process_pdf


# --------------------------------------------------
# Environment
# --------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured"
    )


# --------------------------------------------------
# Gemini
# --------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# --------------------------------------------------
# FastAPI
# --------------------------------------------------

app = FastAPI(
    title="GenAI Student Assistant",
    description="RAG-powered student AI assistant",
    version="2.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Request Model
# --------------------------------------------------

class Message(BaseModel):
    role: str
    text: str


class QuestionRequest(BaseModel):
    question: str
    history: list[Message] = []


# --------------------------------------------------
# Home
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "GenAI Student Assistant RAG API is running"
    }


# --------------------------------------------------
# Ask Question
# --------------------------------------------------
@app.post("/ask")
def ask_ai(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    try:

        # ------------------------------------------
        # Step 1: Search the PDF
        # ------------------------------------------

        results = search_documents(
            question,
            top_k=5
        )

        # ------------------------------------------
        # Step 2: Prepare document context
        # ------------------------------------------

        context_parts = []

        for result in results:

            context_parts.append(
                f"""
--- Document Section {result['chunk_id']} ---
{result['text']}
"""
            )

        context = "\n".join(context_parts)

        # ------------------------------------------
        # Step 3: Prepare conversation history
        # ------------------------------------------

        conversation = ""

        for message in request.history[-10:]:

            role = (
                "Student"
                if message.role == "user"
                else "Assistant"
            )

            conversation += (
                f"{role}: {message.text}\n"
            )

        # ------------------------------------------
        # Step 4: RAG + Conversation prompt
        # ------------------------------------------

        prompt = f"""
You are a helpful college Student AI Assistant.

Your job is to help students understand
their academic study material.

Use the provided document context to answer
the student's question.

You also have access to the recent conversation
history so you can understand follow-up questions.

IMPORTANT RULES:

1. Use the document context as your primary source.
2. Use conversation history to understand context.
3. Do not invent information.
4. If the answer cannot be found in the provided
   study material, say:

   "I couldn't find this information
   in the provided study material."

5. Explain difficult concepts simply.
6. Give examples when useful.
7. Keep answers clear and concise.

RECENT CONVERSATION:

{conversation}

CURRENT STUDENT QUESTION:

{question}

DOCUMENT CONTEXT:

{context}
"""

        # ------------------------------------------
        # Step 5: Gemini
        # ------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        # ------------------------------------------
        # Step 6: Sources
        # ------------------------------------------

        sources = []

        for result in results:

            sources.append({
                "chunk_id": result["chunk_id"],
                "similarity": round(
                    result["score"],
                    4
                )
            })

        # ------------------------------------------
        # Step 7: Return response
        # ------------------------------------------

        return {
            "question": question,
            "answer": response.text,
            "sources": sources
        }

    except Exception as e:

        print("ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    # ------------------------------------------
    # Validate file type
    # ------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # ------------------------------------------
    # Create upload folder
    # ------------------------------------------

    upload_folder = Path("uploads")

    upload_folder.mkdir(
        exist_ok=True
    )

    # ------------------------------------------
    # Save uploaded PDF
    # ------------------------------------------

    file_path = (
        upload_folder /
        file.filename
    )

    contents = await file.read()

    file_path.write_bytes(
        contents
    )

    # ------------------------------------------
    # Process PDF
    # ------------------------------------------

    try:

        result = process_pdf(
            file_path
        )

        return {
            "message": "PDF uploaded and processed successfully",
            **result
        }

    except Exception as e:

        print("UPLOAD ERROR:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )