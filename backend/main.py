import os
import logging
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import httpx

# Local modules
from safety import SafetyLayer
from rag import RAGPipeline

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

# Base directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "gita.json")
CACHE_PATH = os.path.join(BASE_DIR, "data_cache")

# Load Environment Variables
from dotenv import load_dotenv
load_dotenv(os.path.join(BASE_DIR, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    GROQ_API_KEY = GROQ_API_KEY.strip()
else:
    logger.warning("GROQ_API_KEY is not set. LLM features will fail.")

DEPRECATED_MODELS = {"llama-3.1-8b-instant", "llama3-8b-8192", "llama-3-8b-8192", "llama-3.3-70b-versatile"}
configured_model = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b").strip()
if configured_model in DEPRECATED_MODELS:
    logger.warning(f"Configured model '{configured_model}' is deprecated. Defaulting to 'qwen/qwen3.8-27b'.")
    GROQ_MODEL = "qwen/qwen3.8-27b"
else:
    GROQ_MODEL = configured_model

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Global instances
rag: Optional[RAGPipeline] = None
safety: Optional[SafetyLayer] = None
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global rag, safety, http_client

    logger.info("Starting up GitaGuide AI backend...")
    
    # Initialize Safety Layer
    safety = SafetyLayer()
    
    # Initialize RAG Pipeline
    rag = RAGPipeline()
    try:
        await rag.ingest_data(json_path=DATA_PATH, index_path=CACHE_PATH)
    except Exception as e:
        logger.error(f"Failed to ingest data: {e}")
    
    # Initialize HTTP Client for shared connection pooling
    http_client = httpx.AsyncClient(timeout=30.0)
    
    yield
    
    logger.info("Shutting down GitaGuide AI backend...")
    if http_client:
        await http_client.aclose()


app = FastAPI(lifespan=lifespan, title="GitaGuideAI API")

# Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to GitaGuideAI API",
        "docs": "/docs",
        "health": "/health",
        "model": GROQ_MODEL
    }

# Pydantic Models
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    mood: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    relevant_verses: List[dict]
    language: str

# Helper: Call LLM with automatic failover
async def call_llm(context: str, query: str, mood: str, language: str) -> str:
    """Calls Groq API to generate response with automatic fallback models."""
    if not GROQ_API_KEY:
        return "Using a placeholder response because GROQ_API_KEY is not set."

    system_prompt = (
        "You are GitaGuide AI, a warm spiritual companion grounded in the Bhagavad Gita.\n"
        "IMPORTANT FORMATTING RULES:\n"
        "1. Give ONLY your guidance, explanation, and practical advice in your response.\n"
        "2. Do NOT include verse text, Sanskrit shlokas, or transliterations in your reply -- these are shown separately in the UI.\n"
        "3. You may briefly mention a verse reference like 'Chapter 2, Verse 47' for context, but do NOT quote the full verse.\n"
        "4. Keep your reply concise, warm, and conversational -- like a wise friend, not a textbook.\n"
        "5. Structure: Brief insight -> Practical reflection -> Gentle encouragement.\n"
        f"6. Adapt tone based on user mood: {mood or 'neutral'}.\n"
        "7. If the question is outside scope, say: 'The Bhagavad Gita does not directly address this.'\n"
        "8. Do not provide medical, legal, or financial advice.\n"
        "9. If user expresses self-harm intent, respond supportively and encourage professional help.\n"
        f"10. Respond fully in: {language}.\n"
    )
    
    user_message = f"Context from Bhagavad Gita:\n{context}\n\nUser Question: {query}"

    candidates = [GROQ_MODEL, "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]
    seen = set()
    models_to_try = [m for m in candidates if not (m in seen or seen.add(m))]

    last_error = None
    for model_name in models_to_try:
        try:
            response = await http_client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 600
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            last_error = e
            logger.warning(f"Groq model {model_name} failed: {e}. Trying next candidate...")
            continue

    logger.error(f"All LLM Calls failed: {last_error}")
    return f"I am currently meditating on your question. Please try again. (Issue: {str(last_error)})"

from langdetect import detect, LangDetectException

# Helper: Translate to English with automatic failover
async def translate_to_english(text: str) -> str:
    """Translates text to English using Groq LLM."""
    if not GROQ_API_KEY:
        return text 

    system_prompt = "You are a precise translator. Translate the user's text to English. Return ONLY the English translation, no acknowledgement."
    
    candidates = [GROQ_MODEL, "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
    seen = set()
    models_to_try = [m for m in candidates if not (m in seen or seen.add(m))]

    for model_name in models_to_try:
        try:
            response = await http_client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ],
                    "temperature": 0.1,
                    "max_tokens": 300
                }
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Translation with {model_name} failed: {e}")
            continue

    return text

@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_endpoint(request: Request, chat_req: ChatRequest):
    user_text = chat_req.message.strip()
    if not user_text:
        return ChatResponse(
            response="Please share what is on your mind or in your heart.",
            relevant_verses=[],
            language=chat_req.language
        )
    
    # 0. Language Detection
    detected_lang = "en"
    try:
        detected_lang = detect(user_text)
    except LangDetectException:
        pass
        
    # 1. Translate if needed (for Safety & RAG)
    english_text = user_text
    if detected_lang != "en":
        english_text = await translate_to_english(user_text)
        logger.info(f"Translated '{user_text}' ({detected_lang}) -> '{english_text}'")

    # 2. Safety Check (on English text)
    safety_result = await safety.check_input(english_text)
    if not safety_result["safe"]:
        return ChatResponse(
            response=safety_result["message"], 
            relevant_verses=[], 
            language=chat_req.language
        )
        
    # 3. RAG Retrieval (on English text)
    cleaned_query = safety.sanitize(english_text)
    retrieved_docs = await rag.search(cleaned_query, limit=3)
    
    context_text = "\n\n".join([f"Verse {d['metadata']['chapter']}.{d['metadata']['verse']}: {d['content']}" for d in retrieved_docs])
    verses_metadata = [d['metadata'] for d in retrieved_docs]
    
    # 4. LLM Generation
    combined_query = f"Original Query ({detected_lang}): {user_text}\nUnderstood Meaning: {english_text}"
    
    ai_response = await call_llm(
        context=context_text, 
        query=combined_query, 
        mood=chat_req.mood, 
        language=chat_req.language
    )
    
    return ChatResponse(
        response=ai_response,
        relevant_verses=verses_metadata,
        language=chat_req.language
    )

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "verses_loaded": len(rag.documents) if rag else 0,
        "model": GROQ_MODEL
    }
