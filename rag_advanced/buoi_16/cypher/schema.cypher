// Schema & Index cho Knowledge Graph mini Buổi 14
CREATE CONSTRAINT cstr_vanban_id IF NOT EXISTS FOR (v:VanBan) REQUIRE v.id IS UNIQUE;
CREATE CONSTRAINT cstr_dieukhoan_id IF NOT EXISTS FOR (d:DieuKhoan) REQUIRE d.id IS UNIQUE;
CREATE INDEX idx_session IF NOT EXISTS FOR (n:VanBan) ON (n.lab_session);