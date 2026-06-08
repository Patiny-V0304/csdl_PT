import sqlite3

# Kết nối tới CSDL gốc
conn = sqlite3.connect("site_a_local.db")
cursor = conn.cursor()

print("🔍 BẢNG ORIGINAL_RECORDS (In thử 3 dòng đầu tiên):")
cursor.execute("SELECT * FROM original_records LIMIT 3")
rows = cursor.fetchall()
for row in rows:
    print(f"OID: {row[0]} | Record ID: {row[1]} | Meta: {row[2]} | Score: {row[3]:.2f}")

print("\n🔍 BẢNG ORIGINAL_LOGS (In thử 5 dòng log đầu tiên):")
cursor.execute("SELECT * FROM original_logs LIMIT 5")
logs = cursor.fetchall()
for log in logs:
    print(f"ID: {log[0]} | Belong to OID: {log[1]} | Event: {log[2]} | Status: {log[3]}")

conn.close()