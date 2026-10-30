"""DocuMind Pro — LangChain 1.x (No Memory Glitch)."""
import streamlit as st
from langgraph.types import Command

from config import settings
from core.agent_factory import build_agent
from core.rag_pipeline import build_vectorstore, get_file_id

BANNED = ["reveal your api key", "ignore previous instructions", "system prompt",
          "print secrets", "make a bomb", "hack"]

st.set_page_config(page_title="DocuMind Pro", page_icon="🤖", layout="centered")

# State
D = {"messages": [], "session_id": "session_v99", "vectorstore": None,
     "holder": {"vs": None}, "pdf_id": None, "pdf_name": None, "language": "English",
     "last_result": None}
for k, v in D.items():
    st.session_state.setdefault(k, v)

st.session_state.holder["vs"] = st.session_state.vectorstore

# Sidebar
with st.sidebar:
    st.header("📄 DocuMind Pro")
    file = st.file_uploader("Upload a PDF (Optional)", type="pdf")
    lang = st.selectbox("🌐 Response Language", list(settings.LANGUAGES))
    st.session_state.language = settings.LANGUAGES[lang]
    
    # Jab New Chat dabao, toh memory puri tarah clear ho jaye
    if st.button("➕ New chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.session_state.session_id = "session_v99_new" 
        st.rerun()

# UI
st.title("📄 DocuMind Pro")
st.info("💡 Chat freely, search the web, or upload a PDF.")
st.write(f"**Language:** {st.session_state.language}")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

agent = build_agent(st.session_state.language, st.session_state.holder)
cfg = {"configurable": {"thread_id": st.session_state.session_id}}

# Interrupt Check
result = st.session_state.get("last_result")
interrupts = getattr(result, "interrupts", None) if result else None

if interrupts:
    intr = interrupts[0]
    payload = intr.value if hasattr(intr, "value") else {}
    
    st.warning("⚠️ **Approval Required:** Agent wants to send an email.")
    action_reqs = payload.get("action_requests", []) if isinstance(payload, dict) else []
    if action_reqs:
        args = action_reqs[0].get("args", {})
        st.markdown(f"**To:** `{args.get('recipient','N/A')}`  \n"
                    f"**Subject:** `{args.get('subject','N/A')}`  \n"
                    f"**Message:** {args.get('message','N/A')}")

    c1, c2 = st.columns(2)
    
    if c1.button("✅ Approve & Send", use_container_width=True):
        with st.spinner("Sending Email..."):
            try:
                # 1. Agent ko bolo ki approve karo (yeh sirf graph ko aage badhayega)
                agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=cfg, version="v2")
                
                # 2. Bypass LLM: Seedha apna tool call karo aur asli result lo
                from core.tools import send_email
                args = action_reqs[0].get("args", {})
                
                # Yeh line actually email bhejegi aur exact result/error degi
                actual_result = send_email.invoke(args)
                
                # 3. Result ko chat mein add karo
                st.session_state.messages.append({"role": "assistant", "content": str(actual_result)})
                st.session_state.last_result = None # Interrupt clear karo
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ System Error: {e}")

    if c2.button("❌ Reject", use_container_width=True):
        with st.spinner("Cancelling..."):
            try:
                res = agent.invoke(Command(resume={"decisions": [{"type": "reject", "message": "User rejected"}]}), config=cfg, version="v2")
                st.session_state["last_result"] = res
                st.session_state.messages.append({"role": "assistant", "content": "Email cancelled by user."})
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {e}")
else:
    if q := st.chat_input("Ask a question, search the web, or upload a PDF..."):
        if any(b in q.lower() for b in BANNED):
            st.error("🛡️ Guardrail: Request violates security policy.")
        else:
            st.session_state.messages.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        res = agent.invoke({"messages": [("human", q)]}, config=cfg, version="v2")
                        st.session_state["last_result"] = res
                        if getattr(res, "interrupts", None):
                            st.rerun()
                        if res and res.value and "messages" in res.value:
                            ans = res.value["messages"][-1].content
                            st.markdown(ans)
                            st.session_state.messages.append({"role": "assistant", "content": ans})
                    except Exception as e:
                        st.error(f"❌ Error: {e}")