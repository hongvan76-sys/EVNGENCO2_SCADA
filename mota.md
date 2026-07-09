# Mô Tả Dữ Liệu Vận Hành Hệ Thống HPC

## 1. Tổng Quan
Hệ thống sẽ sử dụng các file dữ liệu vận hành được cập nhật theo từng tháng trong năm 2025. Mỗi file chứa thông tin chi tiết về hoạt động hệ thống với hai cột dữ liệu chính: thời gian (`timestamp`) và sản lượng (`sản lượng`).

## 2. Cấu Trúc Dữ Liệu

### 2.1 Cột Dữ Liệu
Mỗi file dữ liệu vận hành bao gồm 02 cột chính:

- **Cột 1 - Timestamp**: Thời gian ghi nhận dữ liệu
- **Cột 2 - Sản lượng**: Giá trị sản lượng tại thời điểm ghi nhận

### 2.2 Chi Tiết Timestamp
- **Tần suất cập nhật**: Mỗi 10 phút (10 phút/lần)
- **Khoảng thời gian**: Từ ngày 01/01/2025 đến ngày 31/12/2025 (toàn bộ năm 2025)
- **Định dạng**: YYYY-MM-DD HH:MM:SS (ví dụ: 2025-01-01 00:00:00, 2025-01-01 00:10:00, v.v.)
- **Số lượng bản ghi dự kiến**: Khoảng 52,560 bản ghi/năm (365 ngày × 24 giờ × 6 lần/giờ)

### 2.3 Chi Tiết Sản Lượng
- **Phạm vi giá trị**: Nằm trong khoảng từ 0 đến 3000 đơn vị sản lượng
  - Giá trị tối thiểu: 0 (ngừng hoạt động hoặc bảo trì)
  - Giá trị tối đa: 3000 (công suất tối đa của hệ thống)
- **Loại dữ liệu**: Số nguyên hoặc số thập phân (tùy thuộc vào đơn vị tính)
- **Ý nghĩa**: Biểu thị hiệu suất, năng lượng, hoặc khối lượng sản xuất của hệ thống HPC

## 3. Cấu Trúc File Dữ Liệu

### 3.1 Qui Ước Đặt Tên File
- Sẽ tạo **12 file CSV** tương ứng với 12 tháng của năm 2025
- **Qui ước đặt tên**: T[X] hoặc T_[X] (X là số thứ tự tháng)
  - Ví dụ:
    - `T1.csv` hoặc `T01.csv` - Tháng 1 (Tháng Giêng)
    - `T2.csv` hoặc `T02.csv` - Tháng 2 (Tháng Hai)
    - `T12.csv` - Tháng 12 (Tháng Mười hai)

### 3.2 Nội Dung File CSV
```
timestamp,sản lượng
2025-01-01 00:00:00,1500
2025-01-01 00:10:00,1520
2025-01-01 00:20:00,1480
...
```

### 3.3 Đặc Điểm Kỹ Thuật Từng File
- **Định dạng**: CSV (Comma Separated Values)
- **Encoding**: UTF-8
- **Dấu phân cách**: Dấu phẩy (,)
- **Dòng tiêu đề**: Có (header row)
- **Kích thước dự kiến**: Khoảng 1-2 MB mỗi file (tuỳ thuộc độ nén)

## 4. Mục Đích Sử Dụng
- Phân tích hiệu suất hệ thống HPC theo từng tháng
- Theo dõi xu hướng hoạt động và sức mạnh tính toán
- Phát hiện các bất thường hoặc sự cố trong quá trình vận hành
- Lập báo cáo thống kê định kỳ
- Dự báo và tối ưu hoá hoạt động hệ thống