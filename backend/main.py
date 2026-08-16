import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

from search import search_documents


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

class QuestionRequest(BaseModel):
    question: str


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
        # Step 1: Search PDF
        # ------------------------------------------

        results = search_documents(
            question,
            top_k=5
        )


        # ------------------------------------------
        # Step 2: Prepare context
        # ------------------------------------------

        context_parts = []

        for result in results:

            context_parts.append(
                f"""
--- Document Section {result['chunk_id']} ---
{result['text']}
"""
            )

        context = "\n".join(
            context_parts
        )


        # ------------------------------------------
        # Step 3: Create RAG prompt
        # ------------------------------------------

        prompt = f"""
You are a helpful college Student AI Assistant.

Answer the student's question using ONLY
the information provided in the document context.

IMPORTANT RULES:

1. Use the document context as your primary source.
2. Do not invent information.
3. If the answer cannot be found in the
   provided context, clearly say:

   "I couldn't find this information
   in the provided study material."

4. Explain difficult concepts in simple language.
5. Give examples when useful.
6. Keep the answer clear and concise.

STUDENT QUESTION:

{question}


DOCUMENT CONTEXT:

{context}
"""


        # ------------------------------------------
        # Step 4: Ask Gemini
        # ------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # ------------------------------------------
        # Step 5: Return answer
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