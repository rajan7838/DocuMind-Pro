# 🤖 DocuMind Pro

Production-grade agentic RAG assistant with **Human-in-the-Loop (HITL)** email approval, **Google Serper live web search**, multi-tool reasoning, and multilingual responses. Built with **LangChain 1.x**, **LangGraph 1.x**, **Groq**, and **Streamlit**.

---

## ✨ Features

- 📄 **PDF RAG** with vector retrieval + embedding-based reranking
- 🌐 **Google Serper live web search** — news, real-time events, latest info beyond LLM training data
- 🧠 **Agentic reasoning** via LangChain 1.x `create_agent` (Groq GPT-OSS-20B)
- 🛑 **HITL interrupts** — sensitive actions (email) require explicit approval using `HumanInTheLoopMiddleware`
- 🛡️ **Guardrails** — blocks jailbreak/prompt-injection patterns
- 🌐 **Multilingual** — English, Hindi, Hinglish
- 🔧 **Tools** — calculator, word count, weather, SMTP email, PDF search, Serper web search

---

## 🖼️ Agent Flow Diagram


```
                        ┌──────────────────────┐
                        │   START (User Query) │
                        └──────────┬───────────┘
                                   ▼
                        ┌──────────────────────┐
                        │   GUARDRAIL CHECK    │
                        └──────────┬───────────┘
                                   │
                        ┌──────────┴──────────┐
                    ❌ BLOCK              ✅ PASS
                        │                     ▼
                  ┌──────────┐      ┌──────────────────┐
                  │  Error   │      │   AGENT NODE     │
                  └──────────┘      │  (LangGraph LLM) │
                                    └────────┬─────────┘
                                             ▼
                                  ┌──────────────────────┐
                                  │  DECISION NODE       │
                                  └──────────┬───────────┘
                    ┌────────────┬───────────┼───────────┬────────────┐
                    ▼            ▼           ▼           ▼            ▼
              ┌──────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐
              │  Direct  │ │Calculator│ │ Weather │ │  PDF    │ │ TAVILY   │
              │  Answer  │ │  Tool    │ │  Tool   │ │  RAG    │ │  Search  │
              └────┬─────┘ └────┬─────┘ └────┬────┘ └────┬────┘ └────┬─────┘
                   │            └────────────┴───────────┘            │
                   │                         ▼                        ▼
                   │              ┌────────────────────┐   ┌──────────────────┐
                   │              │  TOOL RESULT NODE  │   │  LIVE INTERNET   │
                   │              └─────────┬──────────┘   │  (news, prices,  │
                   │                        │              │   real-time)     │
                   │                        └───────────┬──┴──────────────────┘
                   │                                    ▼
                   │                         ┌──────────────────────┐
                   │                         │   LLM SYNTHESIS      │
                   │                         └──────────┬───────────┘
                   └────────────────┬───────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   FINAL ANSWER       │
                         └──────────────────────┘
```

---

## 🌐 Why Google Serper?

> **Serper add karne se aapka agent news, real-time events, aur latest web information ke liye live internet search kar payega, jo plain LLM apne purane training data se nahi de sakta.**
>
> **Flow:** User query aane par agent khud decide karega ki normal jawab dena hai ya Serper tool call karna hai, aur agar call kiya to search results wapas LLM ko milenge jisse final answer banega.

| Before Serper | After Serper |
|---------------|--------------|
| LLM only answers from training cutoff | LLM can fetch **today's** news, prices, events |
| "I don't have real-time data" | Live web results synthesized into answer |
| Static knowledge | Dynamic, verified, up-to-date |

## 📂 Project Structure

```
.
├── app.py                    # Streamlit UI
├── requirements.txt
├── packages.txt
├── .streamlit/secrets.toml   # Local only (gitignored)
├── config/settings.py        # Env/secrets loader
├── core/
│   ├── agent_factory.py      # LangGraph agent + checkpointer
│   ├── rag_pipeline.py       # Chroma + HF embeddings + rerank
│   └── tools.py              # LangChain tools (incl. Serper)
└── scripts/init_db.sql       # Ops reference
```

