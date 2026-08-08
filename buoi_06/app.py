import streamlit as st
from pathlib import Path

from rag import ask, index, status, has_api_key, connect_database

BASE_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="RAG Workshop Demo", layout="centered")

st.title("RAG Workshop Demo")

st.markdown(
    "This demo connects to `rag.py` for indexing, retrieval, and Gemini-based answer generation. "
    "Use the buttons below to build the index or ask a question."
)

with st.sidebar:
    st.header("Actions")
    if st.button("Index documents"):
        try:
            result = index()
            st.success("Index complete")
            st.json(result)
        except Exception as exc:
            st.error(f"Index failed: {exc}")

    if st.button("Check status"):
        try:
            result = status()
            st.info("Index status")
            st.json(result)
        except Exception as exc:
            st.error(f"Status failed: {exc}")

    st.markdown("---")
    st.write("Environment files:")
    st.write(f"`{BASE_DIR / '.env'}`")
    st.write(f"`{BASE_DIR / '.env.example'}`")

    st.markdown("---")
    # Connection / service statuses
    try:
        conn, backend = connect_database()
        db_status = "PostgreSQL (Connected)" if backend == "postgres" else "Local DB (SQLite)"
        if backend == "sqlite":
            conn.close()
    except Exception:
        db_status = "Local DB (SQLite)"
    st.write(f"**Database:** {db_status}")

    try:
        stt = status()
        chroma_count = stt.get("chunks_indexed", 0)
        st.write(f"**ChromaDB:** Embedded Local — {chroma_count} chunks indexed")
    except Exception:
        st.write("**ChromaDB:** Embedded Local")

    api_status = "Có API Key" if has_api_key() else "Thiếu API Key"
    st.write(f"**Gemini API Key:** {api_status}")

st.header("Ask a question")
question = st.text_area("Question", height=120)
col1, col2 = st.columns([1, 1])
with col1:
    k = st.number_input("Top-k retrieval", min_value=1, max_value=10, value=3)
with col2:
    ask_button = st.button("Ask")

if ask_button:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        with st.spinner("Retrieving answer..."):
            try:
                result = ask(question.strip(), k=int(k))
                if "answer" in result:
                    st.subheader("Answer")
                    st.write(result["answer"])
                else:
                    st.info("Answer generation skipped; returning retrieval results.")
                if result.get("retrievals"):
                    st.subheader("Retrieved documents")
                    for item in result["retrievals"]:
                        meta = item.get("metadata", {})
                        source = meta.get("source", "unknown")
                        page = meta.get("page_start")
                        st.markdown(f"**{item.get('chunk_id', '')}** — {source} | Page: {page}")
                        st.write(item.get("text", ""))
                else:
                    st.write("No retrieval results found.")
            except Exception as exc:
                st.error(f"Ask failed: {exc}")

st.markdown("---")
st.caption("This app uses Streamlit and `rag.py` for a small RAG workflow.")
