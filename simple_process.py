#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script xử lý dữ liệu vận hành HPC
Tạo báo cáo cho 4 quý mà không cần thư viện bên ngoài
"""

import csv
import os
import sys
from datetime import datetime
from collections import defaultdict

# Đường dẫn thư mục
input_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(input_dir, 'reports')

# Tạo thư mục reports nếu chưa tồn tại
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'charts'), exist_ok=True)

# Phân chia quý
quarters = {
    'Q1': [1, 2, 3],
    'Q2': [4, 5, 6],
    'Q3': [7, 8, 9],
    'Q4': [10, 11, 12]
}

def load_csv_data(month):
    """Load dữ liệu từ file CSV"""
    filepath = os.path.join(input_dir, f'T{month}.csv')
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp = row['timestamp']
                    production = float(row['sản lượng'])
                    data.append({
                        'timestamp': timestamp,
                        'production': production,
                        'hour': int(timestamp.split(' ')[1].split(':')[0]),
                        'time_slot': ':'.join(timestamp.split(' ')[1].split(':')[:2])
                    })
                except (ValueError, KeyError):
                    pass
        return data
    except Exception as e:
        print(f"Error loading T{month}.csv: {str(e)}", file=sys.stderr)
        return []

def calculate_statistics(data):
    """Calculate statistics"""
    if not data:
        return {}
    
    productions = [d['production'] for d in data]
    total = sum(productions)
    count = len(productions)
    avg = total / count if count > 0 else 0
    max_prod = max(productions)
    min_prod = min(productions)
    
    # Calculate standard deviation
    variance = sum((x - avg) ** 2 for x in productions) / count if count > 0 else 0
    std = variance ** 0.5
    
    return {
        'total': total,
        'average': avg,
        'max': max_prod,
        'min': min_prod,
        'std': std,
        'count': count
    }

def get_hourly_average(data):
    """Get hourly average production"""
    hourly_dict = defaultdict(list)
    for d in data:
        hourly_dict[d['time_slot']].append(d['production'])
    
    hourly = []
    for time_slot in sorted(hourly_dict.keys()):
        avg = sum(hourly_dict[time_slot]) / len(hourly_dict[time_slot])
        hourly.append({'time_slot': time_slot, 'average': avg})
    
    return hourly

def create_simple_chart_html(hourly_data, quarter_name, output_path):
    """Create a simple HTML chart"""
    time_slots = [h['time_slot'] for h in hourly_data]
    averages = [h['average'] for h in hourly_data]
    
    # Simple HTML with embedded SVG-like visualization
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Biểu đồ Sản xuất {quarter_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart {{ border: 1px solid #ccc; padding: 20px; margin: 20px 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #2E86AB; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Biểu đồ Sản xuất trong Ngày - {quarter_name}/2025</h1>
    
    <div class="chart">
        <h2>Dữ liệu Sản lượng Theo Giờ</h2>
        <table>
            <tr>
                <th>Thời gian</th>
                <th>Sản lượng (đơn vị)</th>
                <th>Trực quan</th>
            </tr>
"""
    
    for ts, avg in zip(time_slots, averages):
        # Create a simple bar visualization
        bar_width = int((avg / 3000) * 50)  # Scale to 50 chars
        bar = '█' * bar_width
        html += f"""            <tr>
                <td>{ts}</td>
                <td>{avg:.2f}</td>
                <td>{bar}</td>
            </tr>
"""
    
    html += """        </table>
    </div>
</body>
</html>
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

def generate_quarterly_report(quarter_name, months):
    """Generate report for a quarter"""
    print(f"Processing {quarter_name}...")
    
    # Load all data
    all_data = []
    monthly_data = {}
    monthly_stats = {}
    
    for month in months:
        data = load_csv_data(month)
        if data:
            all_data.extend(data)
            monthly_data[month] = data
            monthly_stats[month] = calculate_statistics(data)
    
    if not all_data:
        print(f"No data for {quarter_name}")
        return
    
    quarterly_stats = calculate_statistics(all_data)
    
    # Create chart HTML
    hourly_data = get_hourly_average(all_data)
    chart_html_path = os.path.join(output_dir, 'charts', f'{quarter_name}_chart.html')
    create_simple_chart_html(hourly_data, quarter_name, chart_html_path)
    
    # Create markdown report
    report_filename = f'BC_{quarter_name}_nam2025.md'
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Báo Cáo Vận Hành HPC - {quarter_name}/2025\n\n")
        f.write(f"**Ngày tạo báo cáo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        # Part I: Statistics
        f.write("## I. Thống Kê Tổng Sản Lượng\n\n")
        f.write("| Chỉ Số | Giá Trị | Ghi Chú |\n")
        f.write("|--------|--------|--------|\n")
        f.write(f"| Tổng sản lượng | {quarterly_stats['total']:,.0f} | Tổng sản lượng toàn quý |\n")
        f.write(f"| Sản lượng trung bình | {quarterly_stats['average']:.2f} | Mức hoạt động trung bình |\n")
        f.write(f"| Sản lượng tối đa | {quarterly_stats['max']:.0f} | Công suất tối đa |\n")
        f.write(f"| Sản lượng tối thiểu | {quarterly_stats['min']:.0f} | Mức sản xuất thấp nhất |\n")
        f.write(f"| Độ lệch chuẩn | {quarterly_stats['std']:.2f} | Mức biến động |\n")
        f.write(f"| Số bản ghi | {quarterly_stats['count']:,.0f} | Tổng số lần cập nhật |\n\n")
        
        # Part II: Chart
        f.write("## II. Biểu Đồ Sản Xuất Trong Ngày\n\n")
        f.write(f"Xem biểu đồ chi tiết: [charts/{quarter_name}_chart.html](charts/{quarter_name}_chart.html)\n\n")
        f.write("### Phân Tích:\n")
        f.write(f"- **Sản lượng trung bình trong ngày:** {quarterly_stats['average']:.2f} đơn vị\n")
        f.write(f"- **Sản lượng cao nhất:** {quarterly_stats['max']:.0f} đơn vị\n")
        f.write(f"- **Sản lượng thấp nhất:** {quarterly_stats['min']:.0f} đơn vị\n")
        f.write(f"- **Đường cảnh báo:** 1000 đơn vị (nếu sản lượng dưới mức này cần kiểm tra)\n")
        f.write(f"- **Biến động:** Sản lượng dao động từ {quarterly_stats['min']:.0f} đến {quarterly_stats['max']:.0f} với độ lệch chuẩn {quarterly_stats['std']:.2f}\n\n")
        
        # Part III: Monthly Comparison
        f.write("## III. So Sánh Sản Lượng Các Tháng\n\n")
        f.write("### Bảng So Sánh\n\n")
        f.write("| Tháng | Sản Lượng Trung Bình | Tổng Sản Lượng | Biến Động (%) |\n")
        f.write("|-------|--------------------|----|---------------|\n")
        
        monthly_averages = [monthly_stats[m]['average'] for m in months]
        avg_of_averages = sum(monthly_averages) / len(monthly_averages)
        
        for month in months:
            stats = monthly_stats[month]
            variance = ((stats['average'] - avg_of_averages) / avg_of_averages) * 100
            f.write(f"| Tháng {month} | {stats['average']:.2f} | {stats['total']:,.0f} | {variance:+.2f}% |\n")
        
        f.write(f"\n**Ghi chú:** Biến động (%) được tính so với sản lượng trung bình của quý ({avg_of_averages:.2f})\n\n")
        
        # Best and worst month
        best_month = max(months, key=lambda m: monthly_stats[m]['average'])
        worst_month = min(months, key=lambda m: monthly_stats[m]['average'])
        
        f.write(f"- **Tháng có sản lượng cao nhất:** Tháng {best_month} ({monthly_stats[best_month]['average']:.2f})\n")
        f.write(f"- **Tháng có sản lượng thấp nhất:** Tháng {worst_month} ({monthly_stats[worst_month]['average']:.2f})\n")
        f.write(f"- **Chênh lệch:** {(monthly_stats[best_month]['average'] - monthly_stats[worst_month]['average']):.2f} đơn vị\n\n")
        
        # Part IV: Conclusion
        f.write("## IV. Nhận Xét Và Kết Luận\n\n")
        
        critical_count = sum(1 for d in all_data if d['production'] < 1000)
        critical_percent = (critical_count / len(all_data)) * 100 if all_data else 0
        
        f.write("### Điểm Nổi Bật:\n")
        f.write(f"- Tổng sản lượng {quarter_name}: **{quarterly_stats['total']:,.0f}** đơn vị\n")
        f.write(f"- Mức hoạt động trung bình: **{quarterly_stats['average']:.2f}** đơn vị/10 phút\n")
        f.write(f"- Hiệu suất công suất: **{(quarterly_stats['average']/3000)*100:.1f}%** so với công suất tối đa\n\n")
        
        f.write("### Cảnh Báo:\n")
        f.write(f"- Số lần sản lượng dưới 1000 đơn vị: **{critical_count:,.0f}** lần ({critical_percent:.2f}%)\n")
        
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
    
    print(f"✓ Report created: {report_filename}")

# Main
print("\n" + "="*60)
print("BẮT ĐẦU XỬ LÝ DỮ LIỆU VẬN HÀNH HPC")
print("="*60 + "\n")

for quarter_name, months in quarters.items():
    generate_quarterly_report(quarter_name, months)

print("\n" + "="*60)
print("✓ HOÀN TẤT!")
print("="*60)
print(f"\nBáo cáo được lưu tại: {output_dir}")
print("\nFile tạo ra:")
for q in quarters.keys():
    print(f"  - BC_{q}_nam2025.md")
    print(f"  - charts/{q}_chart.html")
print("\n" + "="*60)
