import os
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

base_dir = Path("D:/du_an_cua_ban/RAG/rag_advanced/buoi_15")
output_pdf_path = base_dir / "outputs" / "Bao_Cao_Phan_Tich_buoi_15_Hybrid_RAG.pdf"

# Đăng ký font Arial có sẵn của Windows để hỗ trợ đầy đủ dấu Tiếng Việt
font_path = "C:/Windows/Fonts/arial.ttf"
font_bold_path = "C:/Windows/Fonts/arialbd.ttf"
font_italic_path = "C:/Windows/Fonts/ariali.ttf"

if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("Arial", font_path))
    pdfmetrics.registerFont(TTFont("Arial-Bold", font_bold_path))
    pdfmetrics.registerFont(TTFont("Arial-Italic", font_italic_path))
    main_font = "Arial"
    bold_font = "Arial-Bold"
    italic_font = "Arial-Italic"
else:
    main_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    italic_font = "Helvetica-Oblique"

doc = SimpleDocTemplate(
    str(output_pdf_path),
    pagesize=A4,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle",
    fontName=bold_font,
    fontSize=16,
    leading=20,
    alignment=1, # Center
    textColor=colors.HexColor("#003366")
)

subtitle_style = ParagraphStyle(
    "SubtitleStyle",
    fontName=italic_font,
    fontSize=11,
    leading=15,
    alignment=1,
    textColor=colors.HexColor("#555555")
)

h1_style = ParagraphStyle(
    "H1Style",
    fontName=bold_font,
    fontSize=13,
    leading=17,
    textColor=colors.HexColor("#003366"),
    spaceBefore=12,
    spaceAfter=6
)

body_style = ParagraphStyle(
    "BodyStyle",
    fontName=main_font,
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor("#222222")
)

bullet_style = ParagraphStyle(
    "BulletStyle",
    fontName=main_font,
    fontSize=9.5,
    leading=13.5,
    leftIndent=15,
    textColor=colors.HexColor("#222222")
)

table_header_style = ParagraphStyle(
    "TableHeaderStyle",
    fontName=bold_font,
    fontSize=9,
    leading=12,
    textColor=colors.white,
    alignment=1
)

table_cell_style = ParagraphStyle(
    "TableCellStyle",
    fontName=main_font,
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor("#222222")
)

elements = []

# Header
elements.append(Paragraph("BÁO CÁO PHÂN TÍCH BẢN CHẤT & KIẾN TRÚC RAG NÂNG CAO", title_style))
elements.append(Spacer(1, 4))
elements.append(Paragraph("Buổi 14: Hybrid Search + Cross-Encoder Reranking & Mini Knowledge Graph", subtitle_style))
elements.append(Spacer(1, 12))

# Mục 1
elements.append(Paragraph("1. BÀI TOÁN THỰC TẾ: VÌ SAO RAG TRUYỀN THỐNG THẤT BẠI?", h1_style))
elements.append(Paragraph("Khi xây dựng trợ lý AI tra cứu văn bản quy phạm pháp luật hoặc quy định ngân hàng, các hệ thống RAG cơ bản thường gặp hai hạn chế lớn:", body_style))
elements.append(Spacer(1, 4))
elements.append(Paragraph("• <b>Nếu chỉ dùng Dense Vector:</b> Hiểu ý nghĩa khái quát nhưng dễ bỏ sót các từ khóa chính xác như số hiệu văn bản (Thông tư 01/2014), số điều (Điều 24), hoặc tên biểu mẫu.", bullet_style))
elements.append(Paragraph("• <b>Nếu chỉ dùng BM25 Keyword:</b> Bắt từ khóa chuẩn nhưng nếu người dùng hỏi bằng từ đồng nghĩa (ví dụ: 'duyệt cho vay' thay vì 'thẩm quyền cấp tín dụng') thì BM25 sẽ bỏ qua hoàn toàn.", bullet_style))
elements.append(Spacer(1, 4))
elements.append(Paragraph("➔ <b>GIẢI PHÁP BUỔI 14:</b> Kết hợp <b>Hybrid Search (BM25 + Dense)</b> bằng thuật toán RRF, chấm điểm lại bằng <b>Cross-Encoder Reranker</b> và bổ trợ cấu trúc từ <b>Knowledge Graph Neo4j</b>.", body_style))
elements.append(Spacer(1, 10))

# Mục 2
elements.append(Paragraph("2. MỤC ĐÍCH & KẾT QUẢ ĐẠT ĐƯỢC CỦA TỪNG BƯỚC", h1_style))

table_data = [
    [
        Paragraph("Bước thực hiện", table_header_style),
        Paragraph("Mã nguồn", table_header_style),
        Paragraph("Mục đích kỹ thuật & nghiệp vụ", table_header_style),
        Paragraph("Kết quả thực tế đạt được", table_header_style)
    ],
    [
        Paragraph("<b>1. Chuẩn hóa Corpus</b>", table_cell_style),
        Paragraph("<code>prepare_corpus.py</code>", table_cell_style),
        Paragraph("Làm sạch HTML, tách văn bản thành từng Điều khoản, gắn mã định danh duy nhất và tạo Citation xuất xứ.", table_cell_style),
        Paragraph("Tạo file <code>chunks_normalized.csv</code> gồm 1.295 chunks từ 15 văn bản làm nguồn chuẩn dùng chung.", table_cell_style)
    ],
    [
        Paragraph("<b>2. BM25 & Dense Baseline</b>", table_cell_style),
        Paragraph("<code>bm25_retriever.py<br/>dense_retriever.py</code>", table_cell_style),
        Paragraph("Xây 2 bộ lọc độc lập: BM25 bắt từ khóa cứng; Dense Vector hiểu ngữ nghĩa qua mô hình ngôn ngữ và lưu cache.", table_cell_style),
        Paragraph("Tạo 2 chuyên gia tìm kiếm: một bên chuyên từ khóa chính xác, một bên chuyên hiểu ngữ cảnh. Lưu <code>dense_embeddings.pkl</code>.", table_cell_style)
    ],
    [
        Paragraph("<b>3. Hợp nhất Hybrid Search</b>", table_cell_style),
        Paragraph("<code>hybrid_retriever.py</code>", table_cell_style),
        Paragraph("Dung hòa ứng viên của BM25 và Dense bằng Reciprocal Rank Fusion (RRF k=60), tránh cộng điểm thô sai lệch.", table_cell_style),
        Paragraph("Đoạn văn vừa đúng từ khóa vừa sát nghĩa được đưa lên cao nhất, không bị thiên lệch một chiều.", table_cell_style)
    ],
    [
        Paragraph("<b>4. Tái xếp hạng Reranker</b>", table_cell_style),
        Paragraph("<code>reranker.py</code>", table_cell_style),
        Paragraph("Dùng Cross-Encoder đọc đồng thời (Câu hỏi + Đoạn văn) để chấm điểm tương quan thực tế.", table_cell_style),
        Paragraph("Đưa điều khoản trả lời trực tiếp lên Top 1. Thấy rõ sự thay đổi giữa bảng Before và After Rerank.", table_cell_style)
    ],
    [
        Paragraph("<b>5. Đánh giá Benchmark</b>", table_cell_style),
        Paragraph("<code>compare_retrieval.py</code>", table_cell_style),
        Paragraph("Đo lường định lượng Hit@1, Hit@3, Hit@5 trên tập câu hỏi chuẩn (Keyword, Semantic, Mixed).", table_cell_style),
        Paragraph("Xuất báo cáo <code>evaluation_report.md</code> chứng minh Hybrid + Rerank đạt hiệu năng cao nhất.", table_cell_style)
    ],
    [
        Paragraph("<b>6. Mini Knowledge Graph</b>", table_cell_style),
        Paragraph("<code>load_mini_kg.py</code>", table_cell_style),
        Paragraph("Mô hình hóa quan hệ: <code>(:VanBan)-[:CONTAINS]->(:DieuKhoan)-[:NEXT]->(:DieuKhoan)</code> trên Neo4j.", table_cell_style),
        Paragraph("Cung cấp Graph Hints bổ trợ, liên kết điều khoản với văn bản cha và các điều khoản kế tiếp.", table_cell_style)
    ],
    [
        Paragraph("<b>7. Streamlit Web App</b>", table_cell_style),
        Paragraph("<code>app.py</code>", table_cell_style),
        Paragraph("Đóng gói pipeline thành giao diện trực quan cho người dùng trải nghiệm tra cứu và so sánh.", table_cell_style),
        Paragraph("Cho phép thử nghiệm 4 mô hình, hiển thị bảng Before/After Rerank và trích dẫn trực tiếp trên web.", table_cell_style)
    ]
]

t = Table(table_data, colWidths=[85, 95, 170, 170])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#003366")),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")])
]))
elements.append(t)
elements.append(Spacer(1, 10))

# Mục 3
elements.append(Paragraph("3. GIÁ TRỊ CỐT LÕI ĐẠT ĐƯỢC", h1_style))
elements.append(Paragraph("• <b>Độ chính xác cao:</b> Hợp nhất sức mạnh của tìm kiếm từ khóa cứng và tìm kiếm ngữ nghĩa tự nhiên.", bullet_style))
elements.append(Paragraph("• <b>Minh bạch xuất xứ (Grounding & Citation):</b> Mọi kết quả đều dẫn chứng đầy đủ văn bản, số hiệu, điều khoản cụ thể.", bullet_style))
elements.append(Paragraph("• <b>Sẵn sàng cho Graph RAG nâng cao:</b> Cấu trúc đồ thị chuẩn bị sẵn sàng cho các bài toán suy luận đa bước (Multi-hop).", bullet_style))

doc.build(elements)
print(f"✔ ĐÃ TẠO FILE PDF THÀNH CÔNG TẠI:\n{output_pdf_path}")
