# backend/main.py - Updated for production
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import logging
from contextlib import asynccontextmanager

# Import local modules
from services.rag_service import RAGService
from models.chat_models import ChatRequest, ChatResponse, SimplifyRequest
from dotenv import load_dotenv
load_dotenv(override=True)

print(">>> .env OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY")[:10])

from config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global RAG service instance
rag_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global rag_service
    settings = get_settings()
    print(">>> settings.openai_api_key =", settings.openai_api_key[:10])

    
    # Set OpenAI API key from environment
    if settings.openai_api_key:
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key
    
    rag_service = RAGService()
    
    try:
        await rag_service.initialize()
        logger.info("RAG service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG service: {e}")
        # Don't raise error - service will fall back to knowledge-based responses
        logger.info("Service will use knowledge-based responses")
    
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="AskHerCare API",
    description="RAG-based chatbot for women's health queries",
    version="1.0.0",
    lifespan=lifespan
)

# Get settings for CORS
settings = get_settings()

# CORS middleware - Updated for production
# In backend/main.py, update CORS to:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "https://askhercare.vercel.app",
        "https://*.vercel.app",
        "https://askhercare-*.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_rag_service() -> RAGService:
    if rag_service is None:
        raise HTTPException(status_code=503, detail="RAG service not initialized")
    return rag_service

@app.get("/health")
async def health_check():
    openai_status = "enabled" if os.getenv("OPENAI_API_KEY") else "disabled"
    return {
        "status": "healthy", 
        "service": "AskHerCare API", 
        "environment": settings.environment,
        "ai_service": openai_status
    }

@app.get("/categories")
async def get_categories():
    """Get available question categories"""
    return {
        "categories": [
            {
                "id": "menstruation",
                "name": "Menstruation",
                "description": "Periods, cycle tracking, symptoms",
                "icon": "🩸"
            },
            {
                "id": "pregnancy",
                "name": "Pregnancy", 
                "description": "Conception, pregnancy care, symptoms",
                "icon": "🤱"
            },
            {
                "id": "pcos",
                "name": "PCOS",
                "description": "Polycystic ovary syndrome",
                "icon": "🫶"
            },
            {
                "id": "birth_control",
                "name": "Birth Control",
                "description": "Contraceptives, family planning", 
                "icon": "💊"
            },
            {
                "id": "first_time_sex",
                "name": "First-time Sex",
                "description": "Sexual health, first experiences",
                "icon": "💕"
            },
            {
                "id": "vaginal_health",
                "name": "Vaginal Health",
                "description": "Infections, hygiene, wellness",
                "icon": "🌸"
            }
        ]
    }

@app.post("/chat")
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Handle chat messages with RAG responses"""
    try:
        response = await rag_service.get_response(
            question=request.message,
            personality_mode=request.personality_mode,
            category=request.category
        )
        
        return ChatResponse(
            message=response["answer"],
            sources=response.get("sources", []),
            confidence=response.get("confidence", 0.8),
            personality_mode=request.personality_mode
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        # Return a friendly error message
        return ChatResponse(
            message="I'm having some trouble right now, but I'm here to help! Could you try asking your question again?",
            sources=[],
            confidence=0.5,
            personality_mode=request.personality_mode
        )

@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Handle streaming chat responses"""
    async def generate_response():
        try:
            async for chunk in rag_service.get_streaming_response(
                question=request.message,
                personality_mode=request.personality_mode,
                category=request.category
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming: {str(e)}")
            yield f"data: {json.dumps({'error': 'Having trouble right now, please try again!'})}\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.post("/simplify")
async def simplify_response(
    request: SimplifyRequest,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Simplify medical response for teens"""
    try:
        simplified = await rag_service.simplify_response(request.text)
        return {"simplified_text": simplified}
    except Exception as e:
        logger.error(f"Error in simplify endpoint: {str(e)}")
        return {"simplified_text": "Let me put that in simpler terms: " + request.text}

@app.post("/explain-term")
async def explain_medical_term(
    request: dict,
    rag_service: RAGService = Depends(get_rag_service)
):
    """Explain medical terminology"""
    try:
        term = request.get("term", "")
        if not term:
            raise HTTPException(status_code=400, detail="Term is required")
        
        explanation = await rag_service.explain_medical_term(term)
        return {"term": term, "explanation": explanation}
    except Exception as e:
        logger.error(f"Error in explain-term endpoint: {str(e)}")
        return {
            "term": request.get("term", ""),
            "explanation": f"This is a medical term. I'd recommend asking your healthcare provider for a detailed explanation!"
        }

if __name__ == "__main__":
    import uvicorn
    # Use environment variables for production
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)