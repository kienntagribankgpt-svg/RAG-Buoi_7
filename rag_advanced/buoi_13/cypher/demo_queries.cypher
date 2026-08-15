// Query A: Xem toàn bộ đồ thị
MATCH (n) OPTIONAL MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100;

// Query B: Tìm kiểm soát giảm thiểu rủi ro RR-001
MATCH (k:KiemSoat)-[r:MITIGATES]->(rr:RuiRo {id: "RR-001"}) RETURN k, r, rr;

// Query C: Tìm sự kiện rủi ro từ RR-001
MATCH (rr:RuiRo {id: "RR-001"})-[r:OBSERVED_AS]->(sk:SuKienRuiRo) RETURN rr, r, sk;

// Query D: Multi-hop (KiemSoat -> RuiRo -> SuKienRuiRo)
MATCH (k:KiemSoat)-[:MITIGATES]->(rr:RuiRo)-[:OBSERVED_AS]->(sk:SuKienRuiRo) RETURN k, rr, sk;

// Query E: Tìm rủi ro không có kiểm soát
MATCH (rr:RuiRo) WHERE NOT ()-[:MITIGATES]->(rr) RETURN rr;

// Query F: Tìm relation chưa VERIFIED
MATCH (source)-[r]->(target) WHERE r.verification_status <> 'VERIFIED' RETURN source, r, target;