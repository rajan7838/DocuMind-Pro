"""PDF ingestion + retrieval + reranking. Uses cloud HF embeddings."""
import hashlib
import os
import tempfile

import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import settings


def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    return HuggingFaceEndpointEmbeddings(
        model=settings.EMBED_MODEL,
        huggingfacehub_api_token=settings.HF_TOKEN,
    )


def get_file_id(pdf_bytes: bytes) -> str:
    return hashlib.md5(pdf_bytes).hexdigest()[:16]


def build_vectorstore(pdf_bytes: bytes, filename: str):
    """Return (vectorstore, was_cached)."""
    embeddings = get_embeddings()
    file_id = get_file_id(pdf_bytes)
    collection_name = f"pdf_{file_id}"

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=settings.PERSIST_DIR,
    )

    if vectorstore.get(limit=1)["ids"]:
        return vectorstore, True

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        pages = PyPDFLoader(tmp_path).load()
    finally:
        os.remove(tmp_path)

    for page in pages:
        page.metadata["source"] = filename

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    ).split_documents(pages)

    if not chunks:
        raise ValueError("No text found. Scanned PDFs require OCR.")

    vectorstore.add_documents(chunks)
    return vectorstore, False


def reranked_retrieve(vectorstore, query: str) -> str:
    """Retrieve top-K, then rerank by cosine similarity. Returns formatted context."""
    if not vectorstore:
        return "No PDF uploaded yet."
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K})
        docs = retriever.invoke(query)
        if not docs:
            return "No results found in the document."

        embeddings = get_embeddings()
        q_vec = np.array(embeddings.embed_query(query))
        doc_vecs = np.array(
            embeddings.embed_documents([d.page_content for d in docs])
        )

        q_vec = q_vec / np.linalg.norm(q_vec)
        doc_vecs = doc_vecs / np.linalg.norm(doc_vecs, axis=1, keepdims=True)
        scores = doc_vecs @ q_vec
        best = docs[int(np.argmax(scores))]

        return (
            f"Source: {best.metadata.get('source', 'PDF')} "
            f"(Page {best.metadata.get('page', 0) + 1})\n"
            f"Content: {best.page_content[:300]}"
        )
    except Exception as e:
        return f"Retrieval error: {e}"