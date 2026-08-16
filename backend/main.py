import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai


# Load environment variables
load_dotenv()

# Get Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")


# Create Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)


# Create FastAPI app
app = FastAPI(
    title="GenAI Student Assistant",
    description="AI assistant for students",
    version="1.0.0"
)


# Allow React frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request model
class QuestionRequest(BaseModel):
    question: str


# Home endpoint
@app.get("/")
def home():
    return {
        "message": "GenAI Student Assistant API is running"
    }


# Ask AI endpoint
@app.post("/ask")
def ask_ai(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty"
        )

    prompt = f"""
You are a helpful college student assistant.

Your job is to help students understand:
- College information
- Academic topics
- Learning materials
- Programming concepts
- Assignments
- General study questions

Rules:
1. Explain things clearly and simply.
2. Use examples whenever useful.
3. If you don't know something, say that you don't know.
4. Do not invent college-specific information.
5. Keep answers useful and reasonably concise.

Student question:

{question}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return {
            "question": question,
            "answer": response.text
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI request failed: {str(e)}"
        )