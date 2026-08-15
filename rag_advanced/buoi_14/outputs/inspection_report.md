# BÁO CÁO KIỂM TRA TIỀN TRẠM (PROMPT 0 - BUỔI 14)

- **Working root**: `D:\du_an_cua_ban\RAG\rag_advanced\buoi_14`
- **Nguồn dữ liệu**: `D:\du_an_cua_ban\RAG\rag_advanced\buoi_10\graph_rag_labs\kb+hops`

### File `metadata.csv`
- **Số dòng**: 15
- **Các cột**: `['id', 'title', 'so_ky_hieu', 'ngay_ban_hanh', 'loai_van_ban', 'ngay_co_hieu_luc', 'ngay_het_hieu_luc', 'nguon_thu_thap', 'ngay_dang_cong_bao', 'nganh', 'linh_vuc', 'co_quan_ban_hanh', 'chuc_danh', 'nguoi_ky', 'pham_vi', 'thong_tin_ap_dung', 'tinh_trang_hieu_luc']`
- **Số giá trị null**: {'id': np.int64(0), 'title': np.int64(0), 'so_ky_hieu': np.int64(0), 'ngay_ban_hanh': np.int64(0), 'loai_van_ban': np.int64(0), 'ngay_co_hieu_luc': np.int64(1), 'ngay_het_hieu_luc': np.int64(14), 'nguon_thu_thap': np.int64(5), 'ngay_dang_cong_bao': np.int64(11), 'nganh': np.int64(3), 'linh_vuc': np.int64(2), 'co_quan_ban_hanh': np.int64(0), 'chuc_danh': np.int64(0), 'nguoi_ky': np.int64(0), 'pham_vi': np.int64(0), 'thong_tin_ap_dung': np.int64(15), 'tinh_trang_hieu_luc': np.int64(0)}

### File `content.csv`
- **Số dòng**: 15
- **Các cột**: `['id', 'content_html']`
- **Số giá trị null**: {'id': np.int64(0), 'content_html': np.int64(0)}

### File `relationships.csv`
- **Số dòng**: 8
- **Các cột**: `['doc_id', 'other_doc_id', 'relationship', 'relationship_type']`
- **Số giá trị null**: {'doc_id': np.int64(0), 'other_doc_id': np.int64(0), 'relationship': np.int64(0), 'relationship_type': np.int64(0)}
