# Cấu hình danh sách vai trò hợp lệ trong hệ thống
ROLES = ["Admin", "HR", "Risk_Manager", "Staff", "Guest"]

ROLE_HIERARCHY = {
    "Admin": ["Admin", "HR", "Risk_Manager", "Staff", "Guest"],
    "HR": ["HR", "Staff", "Guest"],
    "Risk_Manager": ["Risk_Manager", "Staff", "Guest"],
    "Staff": ["Staff", "Guest"],
    "Guest": ["Guest"]
}
