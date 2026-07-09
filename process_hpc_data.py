import csv
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

# Cấu hình matplotlib
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

# Đường dẫn thư mục
input_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(input_dir, 'reports')

# Tạo thư mục reports nếu chưa tồn tại
os.makedirs(output_dir, exist_ok=True)

# Phân chia quý
quarters = {
    'Q1': [1, 2, 3],
    'Q2': [4, 5, 6],
    'Q3': [7, 8, 9],
    'Q4': [10, 11, 12]
}

def load_csv_data(month):
    """Load dữ liệu từ file CSV của một tháng"""
    filepath = os.path.join(input_dir, f'T{month}.csv')
    try:
        df = pd.read_csv(filepath, encoding='utf-8')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['sản lượng'] = pd.to_numeric(df['sản lượng'], errors='coerce')
        df = df.dropna()  # Loại bỏ bản ghi lỗi
        return df
    except Exception as e:
        print(f"Lỗi khi đọc T{month}.csv: {str(e)}")
        return None

def calculate_statistics(df):
    """Tính toán các chỉ số thống kê"""
    return {
        'total': df['sản lượng'].sum(),
        'average': df['sản lượng'].mean(),
        'max': df['sản lượng'].max(),
        'min': df['sản lượng'].min(),
        'std': df['sản lượng'].std(),
        'count': len(df)
    }

def get_hourly_average(df):
    """Tính sản lượng trung bình theo giờ trong ngày"""
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['time_slot'] = df['hour'].astype(str).str.zfill(2) + ':' + df['minute'].astype(str).str.zfill(2)
    
    hourly = df.groupby('time_slot')['sản lượng'].mean().reset_index()
    hourly = hourly.sort_values('time_slot')
    return hourly

def create_daily_chart(df, quarter_name, output_path):
    """Tạo biểu đồ sản xuất trong ngày"""
    hourly_data = get_hourly_average(df)
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Vẽ đường sản lượng
    ax.plot(range(len(hourly_data)), hourly_data['sản lượng'].values, 
            linewidth=2, marker='o', markersize=3, color='#2E86AB', label='Sản lượng')
    
    # Vẽ đường cảnh báo
    ax.axhline(y=1000, color='red', linestyle='--', linewidth=2, label='Mức cảnh báo (1000)')
    
    # Cấu hình biểu đồ
    ax.set_xlabel('Thời gian trong ngày', fontsize=11, fontweight='bold')
    ax.set_ylabel('Sản lượng (đơn vị)', fontsize=11, fontweight='bold')
    ax.set_title(f'Biểu đồ Sản xuất trong Ngày - {quarter_name}/2025', 
                 fontsize=13, fontweight='bold', pad=20)
    
    # Thiết lập trục X
    step = max(1, len(hourly_data) // 12)  # Hiển thị 12 nhãn
    xticks_pos = range(0, len(hourly_data), step)
    xticks_labels = [hourly_data.iloc[i]['time_slot'] if i < len(hourly_data) else '' 
                     for i in xticks_pos]
    ax.set_xticks(xticks_pos)
    ax.set_xticklabels(xticks_labels, rotation=45, ha='right')
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='best', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def create_monthly_comparison_chart(quarter_name, months, monthly_stats, output_path):
    """Tạo biểu đồ so sánh sản lượng trung bình các tháng"""
    month_names = [f'Tháng {m}' for m in months]
    month_averages = [monthly_stats[m]['average'] for m in months]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01']
    bars = ax.bar(month_names, month_averages, color=colors[:len(months)], alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Thêm giá trị trên cột
    for bar, value in zip(bars, month_averages):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=10)
    
    ax.set_ylabel('Sản lượng trung bình (đơn vị)', fontsize=11, fontweight='bold')
    ax.set_title(f'So sánh Sản lượng Trung bình Các Tháng - {quarter_name}/2025', 
                 fontsize=13, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y', linestyle=':')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

def generate_quarterly_report(quarter_name, months):
    """Tạo báo cáo cho một quý"""
    print(f"Đang xử lý {quarter_name}...", end=' ')
    
    # Load dữ liệu cho tất cả tháng trong quý
    all_data = []
    monthly_data = {}
    monthly_stats = {}
    
    for month in months:
        df = load_csv_data(month)
        if df is not None:
            all_data.append(df)
            monthly_data[month] = df
            monthly_stats[month] = calculate_statistics(df)
    
    if not all_data:
        print(f"✗ Không có dữ liệu cho {quarter_name}")
        return
    
    # Kết hợp dữ liệu toàn quý
    quarterly_df = pd.concat(all_data, ignore_index=True)
    quarterly_stats = calculate_statistics(quarterly_df)
    
    # Tạo các biểu đồ
    charts_dir = os.path.join(output_dir, 'charts')
    os.makedirs(charts_dir, exist_ok=True)
    
    daily_chart_path = os.path.join(charts_dir, f'{quarter_name}_daily.png')
    monthly_chart_path = os.path.join(charts_dir, f'{quarter_name}_monthly.png')
    
    create_daily_chart(quarterly_df, quarter_name, daily_chart_path)
    create_monthly_comparison_chart(quarter_name, months, monthly_stats, monthly_chart_path)
    
    # Tạo báo cáo Markdown
    report_filename = f'BC_{quarter_name}_nam2025.md'
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Báo Cáo Vận Hành HPC - {quarter_name}/2025\n\n")
        f.write(f"**Ngày tạo báo cáo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        # Phần I: Thống kê tổng sản lượng
        f.write("## I. Thống Kê Tổng Sản Lượng\n\n")
        f.write("| Chỉ Số | Giá Trị | Ghi Chú |\n")
        f.write("|--------|--------|--------|\n")
        f.write(f"| Tổng sản lượng | {quarterly_stats['total']:,.0f} | Tổng sản lượng toàn quý |\n")
        f.write(f"| Sản lượng trung bình | {quarterly_stats['average']:.2f} | Mức hoạt động trung bình |\n")
        f.write(f"| Sản lượng tối đa | {quarterly_stats['max']:.0f} | Công suất tối đa |\n")
        f.write(f"| Sản lượng tối thiểu | {quarterly_stats['min']:.0f} | Mức sản xuất thấp nhất |\n")
        f.write(f"| Độ lệch chuẩn | {quarterly_stats['std']:.2f} | Mức biến động |\n")
        f.write(f"| Số bản ghi | {quarterly_stats['count']:,.0f} | Tổng số lần cập nhật |\n\n")
        
        # Phần II: Biểu đồ sản xuất trong ngày
        f.write("## II. Biểu Đồ Sản Xuất Trong Ngày\n\n")
        f.write(f"![Biểu đồ sản xuất trong ngày]({os.path.relpath(daily_chart_path, output_dir)})\n\n")
        
        f.write("### Phân Tích:\n")
        f.write(f"- **Sản lượng trung bình trong ngày:** {quarterly_stats['average']:.2f} đơn vị\n")
        f.write(f"- **Sản lượng cao nhất:** {quarterly_stats['max']:.0f} đơn vị\n")
        f.write(f"- **Sản lượng thấp nhất:** {quarterly_stats['min']:.0f} đơn vị\n")
        f.write(f"- **Đường cảnh báo:** 1000 đơn vị (nếu sản lượng dưới mức này cần kiểm tra)\n")
        f.write(f"- **Biến động:** Sản lượng dao động từ {quarterly_stats['min']:.0f} đến {quarterly_stats['max']:.0f} với độ lệch chuẩn {quarterly_stats['std']:.2f}\n\n")
        
        # Phần III: So sánh sản lượng các tháng
        f.write("## III. So Sánh Sản Lượng Các Tháng\n\n")
        f.write("### Bảng So Sánh\n\n")
        f.write("| Tháng | Sản Lượng Trung Bình | Tổng Sản Lượng | Biến Động (%) |\n")
        f.write("|-------|--------------------|----|---------------|\n")
        
        monthly_averages = [monthly_stats[m]['average'] for m in months]
        avg_of_averages = np.mean(monthly_averages)
        
        for month in months:
            stats = monthly_stats[month]
            variance = ((stats['average'] - avg_of_averages) / avg_of_averages) * 100
            f.write(f"| Tháng {month} | {stats['average']:.2f} | {stats['total']:,.0f} | {variance:+.2f}% |\n")
        
        f.write(f"\n**Ghi chú:** Biến động (%) được tính so với sản lượng trung bình của quý ({avg_of_averages:.2f})\n\n")
        
        f.write("### Biểu Đồ So Sánh\n\n")
        f.write(f"![Biểu đồ so sánh sản lượng tháng]({os.path.relpath(monthly_chart_path, output_dir)})\n\n")
        
        # Xác định tháng có sản lượng cao nhất/thấp nhất
        best_month = max(months, key=lambda m: monthly_stats[m]['average'])
        worst_month = min(months, key=lambda m: monthly_stats[m]['average'])
        
        f.write(f"- **Tháng có sản lượng cao nhất:** Tháng {best_month} ({monthly_stats[best_month]['average']:.2f})\n")
        f.write(f"- **Tháng có sản lượng thấp nhất:** Tháng {worst_month} ({monthly_stats[worst_month]['average']:.2f})\n")
        f.write(f"- **Chênh lệch:** {(monthly_stats[best_month]['average'] - monthly_stats[worst_month]['average']):.2f} đơn vị\n\n")
        
        # Phần IV: Nhận xét và kết luận
        f.write("## IV. Nhận Xét Và Kết Luận\n\n")
        
        # Phân tích bất thường
        critical_hours = sum(1 for val in quarterly_df['sản lượng'] if val < 1000)
        critical_percent = (critical_hours / len(quarterly_df)) * 100
        
        f.write("### Điểm Nổi Bật:\n")
        f.write(f"- Tổng sản lượng {quarter_name}: **{quarterly_stats['total']:,.0f}** đơn vị\n")
        f.write(f"- Mức hoạt động trung bình: **{quarterly_stats['average']:.2f}** đơn vị/10 phút\n")
        f.write(f"- Hiệu suất công suất: **{(quarterly_stats['average']/3000)*100:.1f}%** so với công suất tối đa\n\n")
        
        f.write("### Cảnh Báo:\n")
        f.write(f"- Số lần sản lượng dưới 1000 đơn vị: **{critical_hours:,.0f}** lần ({critical_percent:.2f}%)\n")
        
        if critical_percent > 10:
            f.write("- ⚠️ **Cảnh báo:** Tỷ lệ hoạt động dưới mức ngưỡng cao, cần kiểm tra hệ thống\n")
        elif critical_percent > 5:
            f.write("- ℹ️ **Lưu ý:** Có một số giai đoạn hoạt động dưới mức ngưỡng, nên theo dõi thêm\n")
        else:
            f.write("- ✓ Hệ thống hoạt động ổn định trên ngưỡng cảnh báo\n")
        
        f.write("\n### Đề Xuất Cải Tiến:\n")
        f.write("1. Tăng cường bảo trì định kỳ để duy trì hiệu suất ổn định\n")
        f.write("2. Phân tích các giai đoạn có sản lượng thấp để xác định nguyên nhân\n")
        f.write("3. Cân nhắc tối ưu hóa tài nguyên tính toán dựa trên xu hướng sản lượng\n")
        f.write("4. Thiết lập hệ thống cảnh báo tự động khi sản lượng dưới 1000 đơn vị\n\n")
        
        f.write("---\n")
        f.write(f"*Báo cáo được tạo tự động bởi hệ thống phân tích dữ liệu HPC*\n")
    
    print(f"✓ {quarter_name}")

# Chạy xử lý cho tất cả các quý
print("\n" + "="*60)
print("BẮT ĐẦU XỬ LÝ DỮ LIỆU VẬN HÀNH HPC")
print("="*60 + "\n")

for quarter_name, months in quarters.items():
    generate_quarterly_report(quarter_name, months)

print("\n" + "="*60)
print("✓ HOÀN TẤT! Báo cáo đã được tạo")
print("="*60)
print(f"\nTất cả báo cáo được lưu trong thư mục: {output_dir}")
print("\nDanh sách file tạo ra:")
print("  - BC_Q1_nam2025.md")
print("  - BC_Q2_nam2025.md")
print("  - BC_Q3_nam2025.md")
print("  - BC_Q4_nam2025.md")
print("  - charts/Q1_daily.png")
print("  - charts/Q1_monthly.png")
print("  - charts/Q2_daily.png")
print("  - charts/Q2_monthly.png")
print("  - charts/Q3_daily.png")
print("  - charts/Q3_monthly.png")
print("  - charts/Q4_daily.png")
print("  - charts/Q4_monthly.png")
