from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from main import SemanticRAG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 LOAD ONCE (IMPORTANT)
semantic_rag = SemanticRAG()

class Query(BaseModel):
    user_query: str
    k: int

@app.post("/chat")
async def chat(query: Query):
    logger.info("Parameter received")
    logger.info(f"User query: {query.user_query}")
    logger.info(f"Value of k: {query.k}")

    reply = semantic_rag.chatbot_(query.user_query, query.k)
    return {"reply": reply}

@app.get("/")
def health():
    return {"status": "running"}
