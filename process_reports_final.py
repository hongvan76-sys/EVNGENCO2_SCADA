#!/usr/bin/env python
"""
HPC Data Processing Script - Generates quarterly reports from monthly CSV files
"""

import os
import csv
from pathlib import Path
from statistics import mean, stdev
from collections import defaultdict
from datetime import datetime

def read_csv_file(filepath):
    """Read a CSV file and return the data as a list of dictionaries"""
    data = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader:
                for row in reader:
                    data.append(row)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return data

def extract_numeric_value(value):
    """Extract numeric value from a field, handling various formats"""
    if not value:
        return None
    try:
        value = str(value).replace(',', '').replace(' ', '').strip()
        if value == '':
            return None
        return float(value)
    except:
        return None

def calculate_statistics(values):
    """Calculate statistics for a list of values"""
    numeric_values = [v for v in values if v is not None]
    
    if not numeric_values:
        return {
            'total': 0,
            'count': 0,
            'average': 0,
            'max': 0,
            'min': 0,
            'stddev': 0
        }
    
    total = sum(numeric_values)
    count = len(numeric_values)
    average = total / count if count > 0 else 0
    max_val = max(numeric_values)
    min_val = min(numeric_values)
    stddev = stdev(numeric_values) if count > 1 else 0
    
    return {
        'total': total,
        'count': count,
        'average': average,
        'max': max_val,
        'min': min_val,
        'stddev': stddev
    }

def process_quarterly_data(month_files):
    """Process data from multiple month files"""
    all_data = []
    
    for month_file in month_files:
        data = read_csv_file(month_file)
        all_data.extend(data)
    
    return all_data

def generate_markdown_report(quarter_name, month_files, output_dir, month_numbers):
    """Generate a markdown report for a quarter"""
    all_data = process_quarterly_data(month_files)
    
    if not all_data:
        print(f"No data found for {quarter_name}")
        return
    
    # Extract production values
    all_productions = []
    monthly_productions = {m: [] for m in month_numbers}
    hourly_productions = defaultdict(list)
    
    for row in all_data:
        prod_val = extract_numeric_value(row.get('sản lượng'))
        if prod_val is not None:
            all_productions.append(prod_val)
            
            # Parse timestamp to get hour
            timestamp = row.get('timestamp', '')
            try:
                if ' ' in timestamp:
                    time_part = timestamp.split(' ')[1]
                    hour = int(time_part.split(':')[0])
                    hourly_productions[f"{hour:02d}:00"].append(prod_val)
            except:
                pass
    
    # Calculate overall statistics
    stats = calculate_statistics(all_productions)
    
    # Calculate monthly statistics
    monthly_stats = {}
    for row in all_data:
        prod_val = extract_numeric_value(row.get('sản lượng'))
        if prod_val is not None:
            timestamp = row.get('timestamp', '')
            try:
                if '-' in timestamp:
                    month = int(timestamp.split('-')[1])
                    if month in month_numbers:
                        if month not in monthly_stats:
                            monthly_stats[month] = []
                        monthly_stats[month].append(prod_val)
            except:
                pass
    
    # Generate markdown content
    report_lines = []
    report_lines.append(f"# Báo Cáo Vận Hành HPC - {quarter_name}/2025\n")
    report_lines.append(f"\n**Ngày tạo báo cáo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
    
    # Part I: Statistics
    report_lines.append("## I. Thống Kê Tổng Sản Lượng\n\n")
    report_lines.append("| Chỉ Số | Giá Trị | Ghi Chú |\n")
    report_lines.append("|--------|--------|--------|\n")
    report_lines.append(f"| Tổng sản lượng | {stats['total']:,.0f} | Tổng sản lượng toàn quý |\n")
    report_lines.append(f"| Sản lượng trung bình | {stats['average']:.2f} | Mức hoạt động trung bình |\n")
    report_lines.append(f"| Sản lượng tối đa | {stats['max']:.0f} | Công suất tối đa |\n")
    report_lines.append(f"| Sản lượng tối thiểu | {stats['min']:.0f} | Mức sản xuất thấp nhất |\n")
    report_lines.append(f"| Độ lệch chuẩn | {stats['stddev']:.2f} | Mức biến động |\n")
    report_lines.append(f"| Số bản ghi | {stats['count']:,.0f} | Tổng số lần cập nhật |\n\n")
    
    # Part II: Hourly analysis
    report_lines.append("## II. Phân Tích Sản Xuất Theo Giờ Trong Ngày\n\n")
    report_lines.append("| Giờ | Sản Lượng TB | Số Lần | Ghi Chú |\n")
    report_lines.append("|-----|-------------|-------|--------|\n")
    
    for hour_key in sorted(hourly_productions.keys()):
        hour_stats = calculate_statistics(hourly_productions[hour_key])
        warning = ""
        if hour_stats['average'] < 1000:
            warning = "⚠️ Dưới cảnh báo"
        report_lines.append(f"| {hour_key} | {hour_stats['average']:.2f} | {hour_stats['count']} | {warning} |\n")
    
    report_lines.append("\n")
    
    # Part III: Monthly comparison
    report_lines.append("## III. So Sánh Sản Lượng Các Tháng\n\n")
    report_lines.append("| Tháng | Sản Lượng TB | Tổng | Số Bản Ghi | Biến Động (%) |\n")
    report_lines.append("|-------|-------------|------|-----------|---------------|\n")
    
    monthly_avg_values = []
    for month in month_numbers:
        if month in monthly_stats and monthly_stats[month]:
            m_stats = calculate_statistics(monthly_stats[month])
            monthly_avg_values.append(m_stats['average'])
        else:
            m_stats = {'average': 0, 'total': 0, 'count': 0}
    
    avg_of_monthly = sum(monthly_avg_values) / len(monthly_avg_values) if monthly_avg_values else 0
    
    for month in month_numbers:
        if month in monthly_stats and monthly_stats[month]:
            m_stats = calculate_statistics(monthly_stats[month])
            variance = ((m_stats['average'] - avg_of_monthly) / avg_of_monthly * 100) if avg_of_monthly > 0 else 0
            report_lines.append(f"| Tháng {month} | {m_stats['average']:.2f} | {m_stats['total']:,.0f} | {m_stats['count']} | {variance:+.2f}% |\n")
    
    report_lines.append(f"\n**Ghi chú:** Biến động (%) được tính so với sản lượng trung bình của quý ({avg_of_monthly:.2f})\n\n")
    
    # Best and worst month
    if month_numbers:
        best_month = max(month_numbers, key=lambda m: calculate_statistics(monthly_stats.get(m, [])).get('average', 0))
        worst_month = min(month_numbers, key=lambda m: calculate_statistics(monthly_stats.get(m, [])).get('average', 0))
        
        best_stats = calculate_statistics(monthly_stats.get(best_month, []))
        worst_stats = calculate_statistics(monthly_stats.get(worst_month, []))
        
        report_lines.append(f"- **Tháng có sản lượng cao nhất:** Tháng {best_month} ({best_stats['average']:.2f})\n")
        report_lines.append(f"- **Tháng có sản lượng thấp nhất:** Tháng {worst_month} ({worst_stats['average']:.2f})\n")
        report_lines.append(f"- **Chênh lệch:** {(best_stats['average'] - worst_stats['average']):.2f} đơn vị\n\n")
    
    # Part IV: Conclusions
    report_lines.append("## IV. Nhận Xét Và Kết Luận\n\n")
    
    critical_count = sum(1 for v in all_productions if v < 1000)
    critical_percent = (critical_count / len(all_productions) * 100) if all_productions else 0
    
    report_lines.append("### Điểm Nổi Bật:\n")
    report_lines.append(f"- Tổng sản lượng {quarter_name}: **{stats['total']:,.0f}** đơn vị\n")
    report_lines.append(f"- Mức hoạt động trung bình: **{stats['average']:.2f}** đơn vị/10 phút\n")
    report_lines.append(f"- Hiệu suất công suất: **{(stats['average']/3000)*100:.1f}%** so với công suất tối đa\n\n")
    
    report_lines.append("### Cảnh Báo:\n")
    report_lines.append(f"- Số lần sản lượng dưới 1000 đơn vị: **{critical_count:,.0f}** lần ({critical_percent:.2f}%)\n")
    
    if critical_percent > 10:
        report_lines.append("- ⚠️ **Cảnh báo:** Tỷ lệ hoạt động dưới mức ngưỡng cao, cần kiểm tra hệ thống\n")
    elif critical_percent > 5:
        report_lines.append("- ℹ️ **Lưu ý:** Có một số giai đoạn hoạt động dưới mức ngưỡng, nên theo dõi thêm\n")
    else:
        report_lines.append("- ✓ Hệ thống hoạt động ổn định trên ngưỡng cảnh báo\n")
    
    report_lines.append("\n### Đề Xuất Cải Tiến:\n")
    report_lines.append("1. Tăng cường bảo trì định kỳ để duy trì hiệu suất ổn định\n")
    report_lines.append("2. Phân tích các giai đoạn có sản lượng thấp để xác định nguyên nhân\n")
    report_lines.append("3. Cân nhắc tối ưu hóa tài nguyên tính toán dựa trên xu hướng sản lượng\n")
    report_lines.append("4. Thiết lập hệ thống cảnh báo tự động khi sản lượng dưới 1000 đơn vị\n\n")
    
    report_lines.append("---\n")
    report_lines.append("*Báo cáo được tạo tự động bởi hệ thống phân tích dữ liệu HPC*\n")
    
    # Write to file
    output_file = os.path.join(output_dir, f"{quarter_name}.md")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(report_lines))
        print(f"✓ Generated: {quarter_name}.md")
    except Exception as e:
        print(f"✗ Error writing {output_file}: {e}")

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("BẮT ĐẦU XỬ LÝ DỮ LIỆU VẬN HÀNH HPC")
    print("="*60 + "\n")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    reports_dir = os.path.join(current_dir, 'reports')
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
        print(f"✓ Created directory: reports/\n")
    
    quarters = {
        'BC_Q1_nam2025': (['T1.csv', 'T2.csv', 'T3.csv'], [1, 2, 3]),
        'BC_Q2_nam2025': (['T4.csv', 'T5.csv', 'T6.csv'], [4, 5, 6]),
        'BC_Q3_nam2025': (['T7.csv', 'T8.csv', 'T9.csv'], [7, 8, 9]),
        'BC_Q4_nam2025': (['T10.csv', 'T11.csv', 'T12.csv'], [10, 11, 12])
    }
    
    for quarter_name, (month_files, month_numbers) in quarters.items():
        full_paths = [os.path.join(current_dir, f) for f in month_files]
        existing_files = [f for f in full_paths if os.path.exists(f)]
        
        if existing_files:
            print(f"Processing {quarter_name}...", end=' ')
            generate_markdown_report(quarter_name, existing_files, reports_dir, month_numbers)
        else:
            print(f"✗ No data files found for {quarter_name}")
    
    print("\n" + "="*60)
    print("✓ HOÀN TẤT! Báo cáo đã được tạo")
    print("="*60)
    print(f"\nBáo cáo được lưu tại: reports/")
    print("\nDanh sách file tạo ra:")
    print("  - BC_Q1_nam2025.md")
    print("  - BC_Q2_nam2025.md")
    print("  - BC_Q3_nam2025.md")
    print("  - BC_Q4_nam2025.md")
    print("\n" + "="*60)

if __name__ == '__main__':
    main()
