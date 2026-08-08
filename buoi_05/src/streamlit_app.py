import streamlit as st
import json
import os

st.set_page_config(page_title="RAG Foundation - Buổi 5 Visualizer", layout="wide")

st.title("Trực Quan Hoá OCR & Các Chiến Lược Chunking (Buổi 5)")

output_dir = "RAG/rag_foundation/buoi_05/output"
raw_file = os.path.join(output_dir, "raw_extracted.txt")
chunks_file = os.path.join(output_dir, "chunks_result.json")

if not os.path.exists(chunks_file):
    st.warning("Chưa tìm thấy dữ liệu đã xử lý. Hãy chạy file `src/processing.py --write` trước!")
else:
    with open(raw_file, "r", encoding="utf-8") as f:
        raw_text = f.read()
        
    with open(chunks_file, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Văn bản thô đã trích xuất (Unicode NFC)")
        st.text_area("Raw Text", raw_text, height=600)

    with col2:
        st.subheader("So sánh các chiến lược Chunking")
        strategy = st.radio("Chọn chiến lược:", ["Fixed-size", "Semantic", "Hierarchical"], horizontal=True)

        selected_key = strategy.lower().split("-")[0]
        chunks = chunks_data.get(selected_key, [])

        st.metric("Tổng số chunks", len(chunks))
        
        for idx, item in enumerate(chunks):
            header_text = f"Chunk #{idx+1} - ID: {item['chunk_id']} ({item['length']} ký tự)"
            with st.expander(header_text):
                st.write(f"**Source:** {item.get('source', 'N/A')} | **Trang:** {item.get('page_start', 1)}-{item.get('page_end', 1)}")
                st.write(item["text"])
