
# Yêu Cầu Xử Lý Dữ Liệu Vận Hành HPC

## 1. Tổng Quan
Phát triển script Python để phân tích dữ liệu vận hành HPC theo từng quý trong năm 2025, tạo ra báo cáo chi tiết với thống kê, biểu đồ và so sánh hiệu suất.

## 2. Dữ Liệu Đầu Vào

### 2.1 Nguồn Dữ Liệu
- **12 file CSV**: T1.csv, T2.csv, ..., T12.csv (tương ứng 12 tháng năm 2025)
- **Cấu trúc**: Mỗi file có 2 cột (timestamp, sản lượng)
- **Định dạng CSV**: UTF-8 encoding, dấu phân cách là dấu phẩy

### 2.2 Phân Chia Theo Quý
- **Quý 1 (Q1)**: Tháng 1, 2, 3 (T1.csv, T2.csv, T3.csv)
- **Quý 2 (Q2)**: Tháng 4, 5, 6 (T4.csv, T5.csv, T6.csv)
- **Quý 3 (Q3)**: Tháng 7, 8, 9 (T7.csv, T8.csv, T9.csv)
- **Quý 4 (Q4)**: Tháng 10, 11, 12 (T10.csv, T11.csv, T12.csv)

## 3. Yêu Cầu Xử Lý

### 3.1 Xử Lý Dữ Liệu
1. **Load dữ liệu**: Đọc toàn bộ 12 file CSV
2. **Kết hợp dữ liệu**: Gom nhóm các file theo quý
3. **Xử lý lỗi**: Kiểm tra dữ liệu thiếu, giá trị không hợp lệ
4. **Tiền xử lý**: Loại bỏ bản ghi lỗi, chuẩn hóa định dạng timestamp

### 3.2 Yêu Cầu 1: Thống Kê Tổng Sản Lượng

Với **mỗi quý**, tính toán và trình bày các chỉ số:

#### Chỉ Số Thống Kê:
- **Tổng sản lượng (Total Production)**
  - Công thức: SUM(sản lượng) cho toàn bộ quý
  - Đơn vị: Theo đơn vị sản lượng trong dữ liệu

- **Sản lượng trung bình (Average Production)**
  - Công thức: AVERAGE(sản lượng) cho toàn bộ quý
  - Ý nghĩa: Mức hoạt động trung bình

- **Sản lượng tối đa (Maximum Production)**
  - Công thức: MAX(sản lượng) trong quý
  - Ý nghĩa: Công suất tối đa đạt được

- **Sản lượng tối thiểu (Minimum Production)**
  - Công thức: MIN(sản lượng) trong quý
  - Ý nghĩa: Mức sản xuất thấp nhất

- **Độ lệch chuẩn (Standard Deviation)**
  - Công thức: STDEV(sản lượng)
  - Ý nghĩa: Mức biến động của sản lượng

- **Số bản ghi (Record Count)**
  - Tổng số lần cập nhật dữ liệu trong quý

### 3.3 Yêu Cầu 2: Biểu Đồ Sản Xuất Trong Ngày

#### Mô Tả Biểu Đồ:
- **Loại biểu đồ**: Line chart (Biểu đồ đường)
- **Trục X (Thời gian)**:
  - Khung giờ trong ngày: từ 00:00 đến 24:00 (23:50)
  - Chia thành 144 khoảng (cập nhật 10 phút/lần)
  - Format: HH:MM

- **Trục Y (Sản lượng)**:
  - Giá trị sản lượng trung bình trong mỗi khoảng giờ
  - Phạm vi: 0 - 3000 (hoặc max giá trị thực tế)

#### Đường Cảnh Báo (Warning Line):
- **Mức cảnh báo**: 1000 đơn vị sản lượng
- **Kiểu đường**: Đường đứt nét màu đỏ hoặc cam
- **Ý nghĩa**: Đánh dấu mức sản lượng dưới ngưỡng an toàn
- **Giải thích**: Khi sản lượng dưới 1000 cần chú ý kiểm tra hệ thống

#### Thông Tin Biểu Đồ:
- **Tiêu đề**: "Biểu đồ Sản xuất trong Ngày - Quý [X]"
- **Kích thước**: Đủ lớn để dễ nhìn (width: 1200px hoặc tương đương)
- **Legenda**: Ghi chú cho đường sản lượng và đường cảnh báo
- **Grid**: Bật lưới để dễ đọc giá trị

### 3.4 Yêu Cầu 3: So Sánh Sản Lượng Trung Bình Các Tháng Trong Quý

#### Hình Thức So Sánh:
1. **Bảng so sánh (Table)**
   - 3 cột: Tháng, Sản lượng trung bình, Biến động (%)
   - Xếp hạng từ cao đến thấp

2. **Biểu đồ cột (Bar Chart)**
   - Trục X: Tên tháng (T[X])
   - Trục Y: Sản lượng trung bình
   - Màu sắc khác nhau cho mỗi tháng
   - Thêm giá trị trên mỗi cột

#### Phân Tích:
- Tháng có sản lượng cao nhất/thấp nhất
- Độ chênh lệch so với mức trung bình quý
- Tỷ lệ biến động (%) so với mức trung bình quý

## 4. Kết Quả Đầu Ra

### 4.1 Format Báo Cáo
- **Định dạng**: Markdown (.md file)
- **Tên file**: `BC_Q[X]_nam2025.md` (ví dụ: BC_Q1_nam2025.md, BC_Q2_nam2025.md, v.v.)
- **Encoding**: UTF-8

### 4.2 Cấu Trúc Báo Cáo Markdown

```
# Báo Cáo Vận Hành HPC - Quý X/2025

## I. Thống Kê Tổng Sản Lượng
(Bảng với các chỉ số: Tổng, Trung bình, Max, Min, Độ lệch chuẩn, Số bản ghi)

## II. Biểu Đồ Sản Xuất Trong Ngày
(Hình ảnh biểu đồ đường)
- Mô tả biểu đồ
- Nhận xét chi tiết

## III. So Sánh Sản Lượng Các Tháng
(Bảng so sánh + Biểu đồ cột)

## IV. Nhận Xét Và Kết Luận
- Những điểm nổi bật
- Vấn đề/Cảnh báo
- Đề xuất cải tiến
```

### 4.3 Chi Tiết Báo Cáo
- **Số lượng file output**: 4 file báo cáo (1 cho mỗi quý)
- **Danh sách file**: 
  - BC_Q1_nam2025.md
  - BC_Q2_nam2025.md
  - BC_Q3_nam2025.md
  - BC_Q4_nam2025.md
- **Kích thước tổng file**: ~2-5 MB (tùy độ phân giải biểu đồ)

### 4.4 Nội Dung Chi Tiết Mỗi Báo Cáo

#### Phần I: Thống Kê
- Bảng chứa 6 chỉ số chính (Total, Average, Max, Min, Std Dev, Count)

#### Phần II: Biểu Đồ
- 1 Line chart hiển thị sản lượng 10 phút/lần trong ngày
- 1 đường cảnh báo mức 1000
- Mô tả phân tích các khoảng thời gian

#### Phần III: So Sánh
- 1 Bảng so sánh 3 tháng trong quý
- 1 Bar chart so sánh sản lượng trung bình
- Phân tích sự khác biệt giữa các tháng

#### Phần IV: Kết Luận
- Tóm tắt điểm nổi bật
- Cảnh báo (nếu có bất thường)
- Gợi ý tối ưu hóa

## 5. Công Nghệ Sử Dụng

### Thư Viện Python Cần Thiết:
- `pandas`: Xử lý dữ liệu CSV
- `matplotlib` hoặc `plotly`: Vẽ biểu đồ
- `numpy`: Tính toán thống kê
- `python-dateutil`: Xử lý timestamp

### Quy Trình Thực Hiện:
1. Cài đặt thư viện
2. Load dữ liệu từ 12 file CSV
3. Xử lý và làm sạch dữ liệu
4. Tính toán thống kê theo quý
5. Tạo các biểu đồ
6. Tạo báo cáo Markdown
7. Lưu 4 file báo cáo