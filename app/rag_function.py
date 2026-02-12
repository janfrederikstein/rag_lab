import os
from pathlib import Path
from typing import List, Tuple
from functools import lru_cache

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# Paths (same as notebook)
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

if not CHROMA_DIR.exists():
    raise FileNotFoundError(f"Couldn't find chroma_db at: {CHROMA_DIR}")


# Env + model config (same as notebook)
load_dotenv(override=True)

if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        "OPENAI_API_KEY not found. Create a .env file (copy from .env.example) and set OPENAI_API_KEY."
    )

CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")


# Load persisted Chroma (instead of building it)
@lru_cache(maxsize=1)
def load_vectorstore() -> Chroma:
    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Couldn't find {CHROMA_DIR.resolve()}. Run the notebook section that creates the DB first."
        )

    embeddings = OpenAIEmbeddings(
        model=EMBED_MODEL,
        chunk_size=100,
    )

    # Load existing persisted DB
    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    return vectorstore


@lru_cache(maxsize=1)
def load_llm() -> ChatOpenAI:
    return ChatOpenAI(model=CHAT_MODEL, temperature=0)


# RAG prompt + helper funcs (copied from notebook)
RAG_SYSTEM_PROMPT = '''You are a helpful assistant.
Answer the user's question using ONLY the provided context.
If the answer is not contained in the context, say: "I don't know."
Keep the answer concise and clear. Only answer questions about the provided context. Do not use any information that is not in the context.
'''


def format_context(docs: List[Document], max_chars: int = 8000) -> str:
    """Concatenate retrieved chunks into one context string (truncate if needed)."""
    parts = []
    total = 0
    for d in docs:
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", "unknown")
        header = f"\n\n---\nSOURCE: {src} | PAGE: {page}\n"
        text = d.page_content.strip()
        block = header + text
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "".join(parts).strip()


def dedupe_sources(docs: List[Document]) -> List[Tuple[str, int]]:
    seen = set()
    out = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        page = d.metadata.get("page", None)
        key = (src, page)
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def rag_answer(question: str, k: int = 4) -> dict:
    vectorstore = load_vectorstore()
    retriever_k = vectorstore.as_retriever(search_kwargs={"k": k})
    retrieved_docs = retriever_k.invoke(question)

    if not retrieved_docs:
        return {"answer": "I don't know.", "sources": []}

    context = format_context(retrieved_docs)

    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
    ]

    llm = load_llm()
    response = llm.invoke(messages)
    sources = dedupe_sources(retrieved_docs)

    return {"answer": response.content, "sources": sources, "retrieved_docs": retrieved_docs}