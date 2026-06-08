from dataset_generator import fetch_from_sqlite
from serialization_manager import FormatConverter

print("Site B đang cố gắng đọc file storage_payload.json đã bị chỉnh sửa sai lệch...")

# 1. Lấy dữ liệu gốc làm chuẩn
original_dataset = fetch_from_sqlite()

# 2. Site B đọc file từ ổ cứng
with open("storage_payload.json", "rb") as f:
    corrupted_bytes = f.read()

# 3. Tiến hành Rehydrate và đối chiếu
converter = FormatConverter()
rehydrated_data = converter.json_rehydrate(corrupted_bytes)

# 4. Chốt chặn Assert
assert len(rehydrated_data) == len(original_dataset), "LỖI: Mất mát dữ liệu!"
assert rehydrated_data[0].global_oid == original_dataset[0].global_oid, "NGHIÊM TRỌNG: Đụng độ OID hoặc dữ liệu bị giả mạo!"

print("Thành công: Dữ liệu hợp lệ!")