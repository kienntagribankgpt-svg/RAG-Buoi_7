// 1. Xem toàn bộ đồ thị tri thức mini Buổi 14
MATCH (n {lab_session: "buoi_14"})-[r]->(m {lab_session: "buoi_14"})
RETURN n, r, m LIMIT 100;

// 2. Truy vấn từ Văn bản tới các Điều khoản chứa bên trong (CONTAINS)
MATCH (v:VanBan {lab_session: "buoi_14"})-[r:CONTAINS]->(d:DieuKhoan)
RETURN v.id, v.title, d.id, d.article LIMIT 50;

// 3. Truy vấn chuỗi điều khoản liền kề tuần tự (NEXT)
MATCH (d1:DieuKhoan {lab_session: "buoi_14"})-[r:NEXT]->(d2:DieuKhoan {lab_session: "buoi_14"})
RETURN d1.id, d2.id LIMIT 50;

// 4. Truy vấn mối quan hệ pháp lý giữa các văn bản (THAM_CHIEU, THAY_THE, ...)
MATCH (v1:VanBan {lab_session: "buoi_14"})-[r]->(v2:VanBan {lab_session: "buoi_14"})
WHERE type(r) <> "CONTAINS" AND type(r) <> "NEXT"
RETURN v1.id, type(r), v2.id;