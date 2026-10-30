"""Builds the LangChain 1.x agent with HITL middleware."""
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import MemorySaver

from config import settings
from core.tools import calculator, get_weather, send_email, web_search, word_count
from core.rag_pipeline import reranked_retrieve

def _make_pdf_tool(vectorstore_holder: dict):
    @tool
    def query_pdf_document(query: str) -> str:
        """Search uploaded PDF using vector retriever and embedding-based reranking."""
        return reranked_retrieve(vectorstore_holder.get("vs"), query)
    return query_pdf_document

def _get_checkpointer():
    return MemorySaver()

def build_agent(language: str, vectorstore_holder: dict):
    llm = ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0,
    )

    pdf_tool = _make_pdf_tool(vectorstore_holder)
    tools = [calculator, word_count, get_weather, send_email, pdf_tool, web_search]

    prompt = (
        "You are DocuMind Pro, an advanced Agentic AI assistant.\n"
        "RULES:\n"
        "1. PDF question → query_pdf_document\n"
        "2. News/latest/current events → web_search\n"
        "3. Weather → get_weather\n"
        "4. Math → calculator\n"
        "5. SEND EMAIL → ALWAYS call send_email tool. Extract recipient, subject, and message properly.\n"
        "CRITICAL RULE: When extracting the email address, you MUST copy the COMPLETE email address exactly as the user typed it (e.g., 'amitrajan7838@gmail.com'). DO NOT shorten, truncate, or add '...' to the email address.\n"
        "6. General chat → reply directly.\n"
        f"Respond in {language}."
    )

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=prompt,
        checkpointer=_get_checkpointer(),
        middleware=[
            HumanInTheLoopMiddleware(
                interrupt_on={
                    "send_email": {"allowed_decisions": ["approve", "reject"]},
                },
                description_prefix="Email approval required.",
            )
        ],
    )