# 🚀 Object Serialization Comparison: Cross-Platform Sync

> **Đồ án môn Cơ sở dữ liệu phân tán** — Đề tài #90  
> Phân tích Object Serialization Comparison: "Cross-Platform Sync"

---

## 📋 Mô tả dự án

Hệ thống hiện thực và đánh giá sự đánh đổi giữa *tính dễ đọc đối với con người* và *thông lượng mạng* thông qua việc mô phỏng quá trình **đồng bộ hóa chéo nền tảng (Cross-Platform Sync)** của **1.000 đối tượng phức tạp** sử dụng 3 định dạng tuần tự hóa phổ biến:

| Định dạng | Loại | Đặc điểm |
|-----------|------|-----------|
| **JSON** | Text-based | Phổ biến, dễ đọc, được tối ưu ở tầng C-API của Python |
| **XML** | Text-based | Dễ đọc nhất, nhưng chi phí DOM Parsing cao |
| **Protocol Buffers** | Binary | Nhỏ gọn nhất, tốc độ xử lý cao nhất |

---

## 📁 Cấu trúc dự án

```
.
├── dataset_generator.py      # Sinh và lưu trữ 1.000 đối tượng vào SQLite
├── serialization_manager.py  # Lớp FormatConverter: Serialize & Rehydrate
├── benchmark_network.py      # Điều phối mô phỏng & đo benchmark
├── sync_schema.proto         # Đặc tả schema Protocol Buffers
├── sync_schema_pb2.py        # File Python được biên dịch từ .proto
├── site_a_local.db           # Cơ sở dữ liệu SQLite (Site A)
├── storage_payload.json      # Payload JSON (trung chuyển mạng)
├── storage_payload.xml       # Payload XML (trung chuyển mạng)
└── storage_payload.bin       # Payload Binary/Protobuf (trung chuyển mạng)
```

### Mô tả chi tiết các thành phần

**`dataset_generator.py`**  
Khởi tạo Class Hierarchy và quản lý Global OID. Cố định random seed, tự động sinh 1.000 đối tượng phức tạp (chuỗi, số nguyên, số thực, mảng lồng nhau) và lưu vào SQLite theo cấu trúc bảng cha–bảng con.

**`serialization_manager.py`**  
Lớp xử lý trung tâm `FormatConverter` chứa toàn bộ thuật toán Serialize và Rehydrate cho cả 3 định dạng dữ liệu.

**`benchmark_network.py`**  
Điều phối toàn bộ mô phỏng: đo chi phí thời gian CPU (micro-giây), lấy kích thước file vật lý để tính Network Throughput và in báo cáo kết quả.

**`sync_schema.proto` / `sync_schema_pb2.py`**  
Bản đặc tả hợp đồng dữ liệu (Schema) và file Python được biên dịch tự động của Google Protocol Buffers.

---

## ⚙️ Cài đặt

### Yêu cầu

- Python 3.8+
- Các thư viện chuẩn: `json`, `xml`, `sqlite3`, `time`, `os` (không cần cài thêm)

### Cài đặt Protocol Buffers

```bash
pip install protobuf grpcio-tools
```

> **Lưu ý:** File `sync_schema_pb2.py` đã được biên dịch sẵn.  
> Nếu cần biên dịch lại từ file `.proto`:
> ```bash
> python -m grpc_tools.protoc -I. --python_out=. sync_schema.proto
> ```

---

## ▶️ Chạy mô phỏng

```bash
python benchmark_network.py
```

Chương trình sẽ tự động thực hiện toàn bộ pipeline sau:

```
[1] Khởi tạo dữ liệu (Site A)
      └─ Sinh 1.000 đối tượng → ghi vào site_a_local.db

[2] Tuần tự hóa (Serialization)
      └─ Trích xuất từ DB → đúc Object trên RAM → băm thành JSON / XML / Binary

[3] Mô phỏng I/O Mạng
      └─ Ghi 3 payload ra đĩa → đo kích thước vật lý (Byte Size)

[4] Tái tạo đối tượng (Rehydration — Site B)
      └─ Đọc payload → giải nén → ép kiểu thành Object hoàn chỉnh trên RAM

[5] Kiểm tra tính toàn vẹn (Integrity Assert)
      └─ Đối chiếu OID nguồn ↔ đích → phát hiện Collision / mất dữ liệu

[6] Báo cáo Benchmark
      └─ In bảng phân tích tốc độ (ms) và kích thước (KB)
```

---

## 👤 Thông tin nhóm

| | |
|---|---|
| **Sinh viên** | Phan Thiện Vỹ |
| **MSSV** | N23DCCN137 |
| **Lớp** | D23CQCN02-N |
| **Môn học** | Cơ sở dữ liệu phân tán (Distributed Databases) |