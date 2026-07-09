# PowerShell script to generate reports
param(
    [string]$InputDir = $PSScriptRoot,
    [string]$OutputDir = (Join-Path $InputDir "reports")
)

# Create output directory
$null = New-Item -ItemType Directory -Path $OutputDir -Force

# Quarter definitions
$Quarters = @{
    "Q1" = @(1, 2, 3)
    "Q2" = @(4, 5, 6)
    "Q3" = @(7, 8, 9)
    "Q4" = @(10, 11, 12)
}

function Get-CSVData {
    param([int]$Month)
    $FilePath = Join-Path $InputDir "T$Month.csv"
    
    if (Test-Path $FilePath) {
        $Data = @()
        $Reader = New-Object System.IO.StreamReader $FilePath, [System.Text.Encoding]::UTF8
        $Header = $Reader.ReadLine() -split ','
        
        while ($null -ne ($Line = $Reader.ReadLine())) {
            $Values = $Line -split ','
            if ($Values.Count -eq $Header.Count) {
                $Obj = @{}
                for ($i = 0; $i -lt $Header.Count; $i++) {
                    $Obj[$Header[$i].Trim()] = $Values[$i].Trim()
                }
                $Data += $Obj
            }
        }
        $Reader.Close()
        return $Data
    }
    return @()
}

function Get-Statistics {
    param([array]$Data)
    
    if ($Data.Count -eq 0) { return $null }
    
    $Productions = @($Data | ForEach-Object { [double]$_."sản lượng" })
    $Total = $Productions | Measure-Object -Sum | Select-Object -ExpandProperty Sum
    $Average = $Productions | Measure-Object -Average | Select-Object -ExpandProperty Average
    $Max = $Productions | Measure-Object -Maximum | Select-Object -ExpandProperty Maximum
    $Min = $Productions | Measure-Object -Minimum | Select-Object -ExpandProperty Minimum
    
    $Variance = 0
    foreach ($Val in $Productions) {
        $Variance += [Math]::Pow($Val - $Average, 2)
    }
    $Variance /= $Productions.Count
    $StdDev = [Math]::Sqrt($Variance)
    
    return @{
        Total = $Total
        Average = $Average
        Max = $Max
        Min = $Min
        StdDev = $StdDev
        Count = $Productions.Count
    }
}

# Main processing
Write-Host "============================================================"
Write-Host "BẮT ĐẦU XỬ LÝ DỮ LIỆU VẬN HÀNH HPC"
Write-Host "============================================================"
Write-Host ""

foreach ($Quarter in $Quarters.Keys) {
    Write-Host "Processing $Quarter..." -NoNewline
    
    $Months = $Quarters[$Quarter]
    $AllData = @()
    $MonthlyStats = @{}
    
    # Load data for each month
    foreach ($Month in $Months) {
        $Data = Get-CSVData -Month $Month
        $AllData += $Data
        $MonthlyStats[$Month] = Get-Statistics -Data $Data
    }
    
    if ($AllData.Count -eq 0) {
        Write-Host " SKIPPED (no data)"
        continue
    }
    
    # Calculate quarterly statistics
    $QuarterlyStats = Get-Statistics -Data $AllData
    
    # Create report filename
    $ReportFileName = "BC_${Quarter}_nam2025.md"
    $ReportPath = Join-Path $OutputDir $ReportFileName
    
    # Generate Markdown report
    $Report = @"
# Báo Cáo Vận Hành HPC - $Quarter/2025

**Ngày tạo báo cáo:** $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')

## I. Thống Kê Tổng Sản Lượng

| Chỉ Số | Giá Trị | Ghi Chú |
|--------|--------|--------|
| Tổng sản lượng | $("{0:N0}" -f $QuarterlyStats.Total) | Tổng sản lượng toàn quý |
| Sản lượng trung bình | $("{0:N2}" -f $QuarterlyStats.Average) | Mức hoạt động trung bình |
| Sản lượng tối đa | $("{0:N0}" -f $QuarterlyStats.Max) | Công suất tối đa |
| Sản lượng tối thiểu | $("{0:N0}" -f $QuarterlyStats.Min) | Mức sản xuất thấp nhất |
| Độ lệch chuẩn | $("{0:N2}" -f $QuarterlyStats.StdDev) | Mức biến động |
| Số bản ghi | $("{0:N0}" -f $QuarterlyStats.Count) | Tổng số lần cập nhật |

## II. Biểu Đồ Sản Xuất Trong Ngày

### Phân Tích:
- **Sản lượng trung bình trong ngày:** $("{0:N2}" -f $QuarterlyStats.Average) đơn vị
- **Sản lượng cao nhất:** $("{0:N0}" -f $QuarterlyStats.Max) đơn vị
- **Sản lượng thấp nhất:** $("{0:N0}" -f $QuarterlyStats.Min) đơn vị
- **Đường cảnh báo:** 1000 đơn vị (nếu sản lượng dưới mức này cần kiểm tra)
- **Biến động:** Sản lượng dao động từ $("{0:N0}" -f $QuarterlyStats.Min) đến $("{0:N0}" -f $QuarterlyStats.Max) với độ lệch chuẩn $("{0:N2}" -f $QuarterlyStats.StdDev)

## III. So Sánh Sản Lượng Các Tháng

### Bảng So Sánh

| Tháng | Sản Lượng Trung Bình | Tổng Sản Lượng | Biến Động (%) |
|-------|--------------------|----|---------------|
"@
    
    $MonthlyAverages = @()
    foreach ($Month in $Months) {
        $MonthlyAverages += $MonthlyStats[$Month].Average
        $Report += "| Tháng $Month | $("{0:N2}" -f $MonthlyStats[$Month].Average) | $("{0:N0}" -f $MonthlyStats[$Month].Total) | TBD |`n"
    }
    
    $AvgOfAverages = ($MonthlyAverages | Measure-Object -Average).Average
    $Report += "`n**Ghi chú:** Biến động (%) được tính so với sản lượng trung bình của quý ($("{0:N2}" -f $AvgOfAverages))`n`n"
    
    # Find best and worst month
    $BestMonth = $Months | Sort-Object { $MonthlyStats[$_].Average } -Descending | Select-Object -First 1
    $WorstMonth = $Months | Sort-Object { $MonthlyStats[$_].Average } | Select-Object -First 1
    
    $Report += @"
- **Tháng có sản lượng cao nhất:** Tháng $BestMonth ($("{0:N2}" -f $MonthlyStats[$BestMonth].Average))
- **Tháng có sản lượng thấp nhất:** Tháng $WorstMonth ($("{0:N2}" -f $MonthlyStats[$WorstMonth].Average))
- **Chênh lệch:** $("{0:N2}" -f ($MonthlyStats[$BestMonth].Average - $MonthlyStats[$WorstMonth].Average)) đơn vị

## IV. Nhận Xét Và Kết Luận

### Điểm Nổi Bật:
- Tổng sản lượng $Quarter: **$("{0:N0}" -f $QuarterlyStats.Total)** đơn vị
- Mức hoạt động trung bình: **$("{0:N2}" -f $QuarterlyStats.Average)** đơn vị/10 phút
- Hiệu suất công suất: **$("{0:N1}" -f (($QuarterlyStats.Average / 3000) * 100))%** so với công suất tối đa

### Cảnh Báo:
- Số lần sản lượng dưới 1000 đơn vị: TBD

### Đề Xuất Cải Tiến:
1. Tăng cường bảo trì định kỳ để duy trì hiệu suất ổn định
2. Phân tích các giai đoạn có sản lượng thấp để xác định nguyên nhân
3. Cân nhắc tối ưu hóa tài nguyên tính toán dựa trên xu hướng sản lượng
4. Thiết lập hệ thống cảnh báo tự động khi sản lượng dưới 1000 đơn vị

---
*Báo cáo được tạo tự động bởi hệ thống phân tích dữ liệu HPC*
"@
    
    # Write report
    $Report | Out-File -FilePath $ReportPath -Encoding UTF8
    
    Write-Host " ✓"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "✓ HOÀN TẤT! Báo cáo đã được tạo"
Write-Host "============================================================"
Write-Host ""
Write-Host "Báo cáo được lưu tại: $OutputDir"
Write-Host ""
Write-Host "Danh sách file tạo ra:"
foreach ($Q in $Quarters.Keys) {
    Write-Host "  - BC_${Q}_nam2025.md"
}
