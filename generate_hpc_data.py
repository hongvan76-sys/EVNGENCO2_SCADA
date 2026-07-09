import csv
import os
from datetime import datetime, timedelta
import random

# Đặt seed để có thể tái tạo dữ liệu
random.seed(42)

# Đường dẫn thư mục lưu file
output_dir = os.path.dirname(os.path.abspath(__file__))

# Danh sách các tháng và số ngày trong năm 2025
months_days = {
    1: 31,   # Tháng 1
    2: 28,   # Tháng 2 (2025 không phải năm nhuận)
    3: 31,   # Tháng 3
    4: 30,   # Tháng 4
    5: 31,   # Tháng 5
    6: 30,   # Tháng 6
    7: 31,   # Tháng 7
    8: 31,   # Tháng 8
    9: 30,   # Tháng 9
    10: 31,  # Tháng 10
    11: 30,  # Tháng 11
    12: 31   # Tháng 12
}

# Hàm tạo dữ liệu cho một tháng
def generate_monthly_data(year, month, num_days):
    """
    Tạo dữ liệu vận hành cho một tháng
    - Cập nhật mỗi 10 phút
    - Sản lượng từ 0-3000
    """
    data = []
    
    # Thêm header
    data.append(['timestamp', 'sản lượng'])
    
    # Tạo timestamp từ đầu tháng đến cuối tháng
    current_date = datetime(year, month, 1)
    end_date = datetime(year, month, num_days)
    
    # Các giá trị sản lượng mô phỏng (có xu hướng và biến động)
    base_load = 1500  # Mức sản lượng cơ bản
    
    while current_date.date() <= end_date.date():
        # Tạo timestamp mỗi 10 phút
        # Trong một ngày có 24*60/10 = 144 lần cập nhật
        for minute_interval in range(0, 24*60, 10):
            timestamp = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            timestamp = timestamp + timedelta(minutes=minute_interval)
            
            # Sinh sản lượng ngẫu nhiên
            # Có xu hướng cao vào giờ hành chính, thấp vào đêm
            hour = timestamp.hour
            
            # Hệ số biến động theo giờ trong ngày
            if 6 <= hour < 12:  # Sáng
                time_factor = 1.1
            elif 12 <= hour < 18:  # Chiều
                time_factor = 1.2
            elif 18 <= hour < 22:  # Tối
                time_factor = 0.9
            else:  # Đêm
                time_factor = 0.6
            
            # Tính sản lượng với biến động ngẫu nhiên
            load = int(base_load * time_factor + random.gauss(0, 100))
            load = max(0, min(3000, load))  # Giới hạn trong khoảng 0-3000
            
            data.append([timestamp.strftime('%Y-%m-%d %H:%M:%S'), load])
        
        current_date += timedelta(days=1)
    
    return data

# Tạo file CSV cho mỗi tháng
print("Bắt đầu tạo dữ liệu vận hành HPC...")
print("=" * 60)

for month in range(1, 13):
    filename = f"T{month}.csv"
    filepath = os.path.join(output_dir, filename)
    
    num_days = months_days[month]
    data = generate_monthly_data(2025, month, num_days)
    
    # Ghi file CSV
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(data)
        
        num_records = len(data) - 1  # Trừ header
        print(f"✓ {filename:<8} - Tạo thành công ({num_records} bản ghi)")
    except Exception as e:
        print(f"✗ {filename:<8} - Lỗi: {str(e)}")

print("=" * 60)
print(f"✓ Hoàn tất! Tất cả 12 file CSV đã được tạo trong:")
print(f"  {output_dir}")
