# Buổi 09: Multi-query Retrieval và Parent–Child Retrieval

## Tổng quan Pipeline
1. **Query Fan-out**: Nhận câu hỏi gốc Q0, sinh các biến thể Q1..Q3.
2. **Hybrid Search**: Chạy BM25 + Semantic cho từng query.
3. **Cross-Query RRF**: Hợp nhất kết quả child hits từ nhiều query.
4. **Parent-Child Mapping**: Ánh xạ child hit sang parent document (Điều/Khoản).
5. **Parent Reranking**: Rerank lại parent context bằng câu hỏi gốc Q0.
6. **Answer Generation**: Sinh câu trả lời kèm citation [P1], [P2].

## Bốn chế độ (Modes)
- `single_flat`: 1 Query -> Child Chunk -> Rerank Child
- `multi_flat`: Multi Query -> Child Chunk -> Rerank Child
- `single_parent`: 1 Query -> Parent Context -> Rerank Parent
- `multi_parent`: Multi Query -> Parent Context -> Rerank Parent (Mặc định)

## Hình ảnh Thử nghiệm trên Giao diện Streamlit

### 1. Tab Ask Advanced RAG (Hỏi đáp & Citation)
![Ask Advanced RAG](images/tab1_ask.png)

### 2. Tab Query Fan-out (Phân tách Truy vấn Q0..Q3)
![Query Fan-out](images/tab2_fanout.png)

### 3. Tab Parent–Child Explorer (Khám phá Ngữ cảnh)
![Parent-Child Explorer](images/tab3_explorer.png)

### 4. Tab Mode Comparison (So sánh Chế độ)
![Mode Comparison](images/tab4_comparison.png)