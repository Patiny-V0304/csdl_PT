import os
import time
from dataset_generator import generate_1000_objects, save_original_to_sqlite, fetch_from_sqlite
from serialization_manager import FormatConverter

# Import thư viện vẽ biểu đồ
try:
    import matplotlib.pyplot as plt
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("CẢNH BÁO: Chưa cài đặt matplotlib. Vui lòng chạy lệnh: pip install matplotlib numpy")

def run_sync_simulation(format_name, file_ext, serialize_fn, rehydrate_fn, dataset):
    print(f"\n[{format_name}] ĐANG ĐỒNG BỘ...")
    payload_file = f"storage_payload{file_ext}"
    
    # 1. Site A: Serialize & Ghi Payload ra đĩa
    start_ser = time.perf_counter()
    byte_stream = serialize_fn(dataset)
    with open(payload_file, 'wb') as f:
        f.write(byte_stream)
    time_serialize_ms = (time.perf_counter() - start_ser) * 1000
    
    # 2. Network: Đo lường băng thông
    file_size_bytes = os.path.getsize(payload_file)
    
    # 3. Site B: Nhận Payload từ đĩa & Rehydrate (Tái tạo)
    start_reh = time.perf_counter()
    with open(payload_file, 'rb') as f:
        read_stream = f.read()
    rehydrated_data = rehydrate_fn(read_stream)
    time_rehydrate_ms = (time.perf_counter() - start_reh) * 1000
    
    # 4. Assert: Kiểm tra OID và Toàn vẹn dữ liệu
    assert len(rehydrated_data) == len(dataset), "NGHIÊM TRỌNG: Mất mát dữ liệu!"
    assert rehydrated_data[0].global_oid == dataset[0].global_oid, "NGHIÊM TRỌNG: Đụng độ OID!"

    print(f"  -> Trọng tải truyền tải: {file_size_bytes / 1024:.2f} KB (File: {payload_file})")
    print(f"  -> Thời gian Serialize:  {time_serialize_ms:.3f} ms")
    print(f"  -> Thời gian Rehydrate:  {time_rehydrate_ms:.3f} ms")
    
    # TRẢ VỀ SỐ LIỆU ĐỂ VẼ BIỂU ĐỒ
    return file_size_bytes / 1024, time_serialize_ms, time_rehydrate_ms

def generate_tradeoff_chart(formats, byte_sizes, serialize_times, rehydrate_times):
    if not HAS_MATPLOTLIB:
        return
        
    print("\nĐang tự động xuất biểu đồ phân tích (Trade-off Chart)...")
    x = np.arange(len(formats))
    width = 0.25

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Cột Trọng tải mạng (KB)
    rects1 = ax1.bar(x - width, byte_sizes, width, label='Kích thước Payload (KB)', color='#3498db')
    ax1.set_ylabel('Dung lượng mạng (KB)', color='#2980b9', fontsize=11, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#2980b9')

    # Trục thứ 2: Cột thời gian xử lý (ms)
    ax2 = ax1.twinx()
    rects2 = ax2.bar(x, serialize_times, width, label='Serialize Time (ms)', color='#2ecc71')
    rects3 = ax2.bar(x + width, rehydrate_times, width, label='Rehydrate Time (ms)', color='#e74c3c')
    ax2.set_ylabel('Thời gian xử lý CPU (ms)', color='#c0392b', fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#c0392b')

    # Trang trí
    ax1.set_title('SO SÁNH ĐÁNH ĐỔI (TRADE-OFF): KÍCH THƯỚC VS THỜI GIAN', fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x)
    ax1.set_xticklabels(formats, fontsize=12, fontweight='bold')

    # Gộp 2 phần chú thích (Legend)
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)

    # Hiển thị số liệu lên đỉnh các cột
    ax1.bar_label(rects1, padding=3, fmt='%.1f')
    ax2.bar_label(rects2, padding=3, fmt='%.1f')
    ax2.bar_label(rects3, padding=3, fmt='%.1f')

    plt.tight_layout()
    plt.savefig('tradeoff_analysis_chart.png', dpi=300, bbox_inches='tight')
    print("Đã lưu file ảnh: tradeoff_analysis_chart.png")
    
    # Tự động mở cửa sổ biểu đồ lên màn hình
    plt.show()

if __name__ == "__main__":
    print("             HỆ THỐNG MÔ PHỎNG CROSS-PLATFORM SYNC")
    
    raw_data = generate_1000_objects()
    save_original_to_sqlite(raw_data)
    db_dataset = fetch_from_sqlite()
    
    converter = FormatConverter()
    
    # Chuẩn bị mảng để hứng số liệu từ các lần đo
    formats = ['JSON', 'XML', 'Protobuf (Binary)']
    sizes_kb, ser_ms, reh_ms = [], [], []
    
    # 1. Đo lường JSON
    size, s_time, r_time = run_sync_simulation("JSON", ".json", converter.json_serialize, converter.json_rehydrate, db_dataset)
    sizes_kb.append(size); ser_ms.append(s_time); reh_ms.append(r_time)
    
    # 2. Đo lường XML
    size, s_time, r_time = run_sync_simulation("XML", ".xml", converter.xml_serialize, converter.xml_rehydrate, db_dataset)
    sizes_kb.append(size); ser_ms.append(s_time); reh_ms.append(r_time)
    
    # 3. Đo lường PROTOBUF
    size, s_time, r_time = run_sync_simulation("PROTOBUF", ".bin", converter.protobuf_serialize, converter.protobuf_rehydrate, db_dataset)
    sizes_kb.append(size); ser_ms.append(s_time); reh_ms.append(r_time)
    
    print("HOÀN TẤT THỰC NGHIỆM!")
    
    # GỌI HÀM VẼ BIỂU ĐỒ BẰNG CHÍNH MẢNG SỐ LIỆU VỪA ĐO
    generate_tradeoff_chart(formats, sizes_kb, ser_ms, reh_ms)