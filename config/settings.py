"""Central config loader."""
import os
from dotenv import load_dotenv

load_dotenv()

def _get(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key, default)

LLM_MODEL = "openai/gpt-oss-20b"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_API_KEY = _get("GROQ_API_KEY")
HF_TOKEN = _get("HF_TOKEN")
SERPER_API_KEY = _get("SERPER_API_KEY")

PERSIST_DIR = "chroma_db"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3

EMAIL_SENDER = _get("EMAIL_SENDER")
EMAIL_PASSWORD = _get("EMAIL_PASSWORD")

LANGUAGES = {
    "English": "English",
    "Hindi": "Hindi (Devanagari script)",
    "Hinglish": "Hinglish (Hindi written in English letters)",
}

def validate() -> list[str]:
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not HF_TOKEN:
        missing.append("HF_TOKEN")
    if not SERPER_API_KEY:
        missing.append("SERPER_API_KEY")
    return missing