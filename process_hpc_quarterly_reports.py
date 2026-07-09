#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HPC Operational Data Quarterly Report Generator
Processes 12 monthly CSV files (T1-T12) and generates 4 quarterly markdown reports
"""

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from statistics import mean, stdev

# Configuration
MONTHS_PER_QUARTER = {
    'Q1': [1, 2, 3],
    'Q2': [4, 5, 6],
    'Q3': [7, 8, 9],
    'Q4': [10, 11, 12]
}

MONTH_NAMES = {
    1: 'Tháng 1', 2: 'Tháng 2', 3: 'Tháng 3',
    4: 'Tháng 4', 5: 'Tháng 5', 6: 'Tháng 6',
    7: 'Tháng 7', 8: 'Tháng 8', 9: 'Tháng 9',
    10: 'Tháng 10', 11: 'Tháng 11', 12: 'Tháng 12'
}

YEAR = 2025
REPORTS_DIR = 'reports'


def create_reports_directory():
    """Create reports directory if it doesn't exist."""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"✓ Created directory: {REPORTS_DIR}")
    else:
        print(f"✓ Reports directory exists: {REPORTS_DIR}")


def read_csv_file(filename):
    """Read CSV file and return list of data rows."""
    data = []
    try:
        if not os.path.exists(filename):
            print(f"  ⚠ File not found: {filename}")
            return data
        
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp = row.get('timestamp', '').strip()
                    san_luong = row.get('sản lượng', '').strip()
                    
                    if timestamp and san_luong:
                        try:
                            value = float(san_luong)
                            data.append({
                                'timestamp': timestamp,
                                'san_luong': value
                            })
                        except ValueError:
                            pass
                except Exception as e:
                    pass
        
        print(f"  ✓ Read {filename}: {len(data)} records")
        return data
    except Exception as e:
        print(f"  ✗ Error reading {filename}: {e}")
        return data


def load_all_monthly_data():
    """Load data from all 12 monthly CSV files."""
    print("\n=== Loading Monthly Data ===")
    monthly_data = {}
    
    for month in range(1, 13):
        filename = f'T{month}.csv'
        monthly_data[month] = read_csv_file(filename)
    
    return monthly_data


def extract_hour_from_timestamp(timestamp):
    """Extract hour from timestamp string."""
    try:
        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
            try:
                dt = datetime.strptime(timestamp, fmt)
                return dt.hour
            except ValueError:
                continue
        return None
    except:
        return None


def calculate_statistics(values):
    """Calculate statistics for a list of values."""
    if not values:
        return {
            'total': 0,
            'count': 0,
            'average': 0,
            'max': 0,
            'min': 0,
            'std_dev': 0
        }
    
    total = sum(values)
    count = len(values)
    average = total / count if count > 0 else 0
    max_val = max(values)
    min_val = min(values)
    
    try:
        std_dev = stdev(values) if count > 1 else 0
    except:
        std_dev = 0
    
    return {
        'total': total,
        'count': count,
        'average': average,
        'max': max_val,
        'min': min_val,
        'std_dev': std_dev
    }


def analyze_quarter(quarter, months, monthly_data):
    """Analyze data for a quarter."""
    quarter_data = []
    monthly_stats = {}
    hourly_data = {h: [] for h in range(24)}
    
    # Combine all monthly data for the quarter
    for month in months:
        month_values = [d['san_luong'] for d in monthly_data.get(month, [])]
        
        if month_values:
            monthly_stats[month] = calculate_statistics(month_values)
            quarter_data.extend(month_values)
            
            # Collect hourly data
            for record in monthly_data.get(month, []):
                hour = extract_hour_from_timestamp(record['timestamp'])
                if hour is not None:
                    hourly_data[hour].append(record['san_luong'])
    
    # Calculate quarterly statistics
    quarter_stats = calculate_statistics(quarter_data)
    
    # Calculate hourly statistics
    hourly_stats = {}
    for hour in range(24):
        if hourly_data[hour]:
            hourly_stats[hour] = calculate_statistics(hourly_data[hour])
        else:
            hourly_stats[hour] = None
    
    return {
        'quarter_stats': quarter_stats,
        'monthly_stats': monthly_stats,
        'hourly_stats': hourly_stats,
        'months': months
    }


def format_number(value, decimals=2):
    """Format a number with specified decimal places."""
    try:
        return f"{float(value):.{decimals}f}"
    except:
        return str(value)


def generate_markdown_report(quarter, analysis_data):
    """Generate markdown report for a quarter."""
    quarter_stats = analysis_data['quarter_stats']
    monthly_stats = analysis_data['monthly_stats']
    hourly_stats = analysis_data['hourly_stats']
    months = analysis_data['months']
    
    lines = []
    
    # Header
    lines.append(f"# Báo Cáo Quý {quarter[-1]} Năm {YEAR}")
    lines.append("")
    lines.append(f"**Ngày tạo:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    lines.append("")
    
    # Summary Statistics Table
    lines.append("## 1. Thống Kê Tổng Quát")
    lines.append("")
    lines.append("| Chỉ Số | Giá Trị |")
    lines.append("|--------|--------|")
    lines.append(f"| Tổng Sản Lượng | {format_number(quarter_stats['total'], 2)} |")
    lines.append(f"| Trung Bình | {format_number(quarter_stats['average'], 2)} |")
    lines.append(f"| Giá Trị Cao Nhất | {format_number(quarter_stats['max'], 2)} |")
    lines.append(f"| Giá Trị Thấp Nhất | {format_number(quarter_stats['min'], 2)} |")
    lines.append(f"| Độ Lệch Chuẩn | {format_number(quarter_stats['std_dev'], 2)} |")
    lines.append(f"| Số Lượng Bản Ghi | {quarter_stats['count']} |")
    lines.append("")
    
    # Monthly Comparison
    lines.append("## 2. So Sánh Theo Tháng")
    lines.append("")
    lines.append("| Tháng | Tổng | Trung Bình | Max | Min | Số Bản Ghi |")
    lines.append("|-------|------|-----------|-----|-----|------------|")
    
    for month in months:
        if month in monthly_stats:
            stats = monthly_stats[month]
            lines.append(
                f"| {MONTH_NAMES[month]} | {format_number(stats['total'], 2)} | "
                f"{format_number(stats['average'], 2)} | {format_number(stats['max'], 2)} | "
                f"{format_number(stats['min'], 2)} | {stats['count']} |"
            )
    
    lines.append("")
    
    # Hourly Analysis
    lines.append("## 3. Phân Tích Theo Giờ")
    lines.append("")
    lines.append("| Giờ | Trung Bình | Max | Min | Số Lần | Ghi Chú |")
    lines.append("|-----|------------|-----|-----|--------|---------|")
    
    for hour in range(24):
        stats = hourly_stats.get(hour)
        if stats:
            note = ""
            if stats['average'] > quarter_stats['average'] * 1.2:
                note = "Cao hơn 20%"
            elif stats['average'] < quarter_stats['average'] * 0.8:
                note = "Thấp hơn 20%"
            
            lines.append(
                f"| {hour:02d}:00 | {format_number(stats['average'], 2)} | "
                f"{format_number(stats['max'], 2)} | {format_number(stats['min'], 2)} | "
                f"{stats['count']} | {note} |"
            )
    
    lines.append("")
    
    # Analysis and Conclusions
    lines.append("## 4. Kết Luận và Cảnh Báo")
    lines.append("")
    
    if quarter_stats['count'] == 0:
        lines.append("⚠ **Không có dữ liệu** cho quý này.")
    else:
        lines.append(f"- **Tổng sản lượng:** {format_number(quarter_stats['total'], 2)} đơn vị")
        lines.append(f"- **Trung bình mỗi bản ghi:** {format_number(quarter_stats['average'], 2)} đơn vị")
        lines.append(f"- **Biến động:** {format_number(quarter_stats['std_dev'], 2)} đơn vị")
        lines.append("")
        
        # Identify peak hours
        peak_hours = []
        low_hours = []
        
        for hour in range(24):
            stats = hourly_stats.get(hour)
            if stats and stats['average'] > 0:
                if stats['average'] > quarter_stats['average'] * 1.2:
                    peak_hours.append(f"{hour:02d}:00")
                elif stats['average'] < quarter_stats['average'] * 0.8:
                    low_hours.append(f"{hour:02d}:00")
        
        if peak_hours:
            lines.append(f"- **Giờ cao điểm:** {', '.join(peak_hours)}")
        
        if low_hours:
            lines.append(f"- **Giờ sản lượng thấp:** {', '.join(low_hours)}")
        
        # Monthly analysis
        best_month = max(months, key=lambda m: monthly_stats[m]['total'] if m in monthly_stats else 0)
        worst_month = min(months, key=lambda m: monthly_stats[m]['total'] if m in monthly_stats else float('inf'))
        
        if best_month in monthly_stats and worst_month in monthly_stats:
            lines.append(f"- **Tháng tốt nhất:** {MONTH_NAMES[best_month]} "
                        f"({format_number(monthly_stats[best_month]['total'], 2)} đơn vị)")
            lines.append(f"- **Tháng yếu nhất:** {MONTH_NAMES[worst_month]} "
                        f"({format_number(monthly_stats[worst_month]['total'], 2)} đơn vị)")
        
        lines.append("")
        
        # Warnings
        warnings = []
        if quarter_stats['std_dev'] > quarter_stats['average'] * 0.5:
            warnings.append("⚠️ Sản lượng biến động lớn")
        if len(low_hours) > 6:
            warnings.append("⚠️ Nhiều giờ có sản lượng thấp")
        if quarter_stats['count'] < 1000:
            warnings.append("⚠️ Số lượng bản ghi tương đối ít")
        
        if warnings:
            lines.append("### Cảnh báo:")
            for warning in warnings:
                lines.append(f"- {warning}")
        else:
            lines.append("### Tình trạng: Bình thường ✓")
    
    lines.append("")
    lines.append("---")
    lines.append(f"*Báo cáo được tạo tự động lúc {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*")
    
    return "\n".join(lines)


def save_report(quarter, content):
    """Save report to markdown file."""
    filename = f"BC_{quarter}_nam{YEAR}.md"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Saved report: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error saving {filename}: {e}")
        return False


def main():
    """Main execution function."""
    print("=" * 60)
    print("HPC OPERATIONAL DATA QUARTERLY REPORT GENERATOR")
    print("=" * 60)
    
    # Create reports directory
    create_reports_directory()
    
    # Load all monthly data
    monthly_data = load_all_monthly_data()
    
    # Process each quarter
    print("\n=== Processing Quarters ===")
    total_reports = 0
    
    for quarter_name, months in MONTHS_PER_QUARTER.items():
        print(f"\nProcessing {quarter_name}...")
        
        # Analyze quarter data
        analysis = analyze_quarter(quarter_name, months, monthly_data)
        
        # Generate markdown report
        report_content = generate_markdown_report(quarter_name, analysis)
        
        # Save report
        if save_report(quarter_name, report_content):
            total_reports += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"COMPLETED: {total_reports}/4 quarterly reports generated")
    print(f"Reports saved in: {os.path.abspath(REPORTS_DIR)}")
    print("=" * 60)
    
    return total_reports == 4


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
