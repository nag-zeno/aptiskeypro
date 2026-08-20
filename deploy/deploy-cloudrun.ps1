# ==============================================================================
# Script Triển khai AptisKey lên Google Cloud Run (PowerShell cho Windows)
# ==============================================================================

param (
    [string]$ProjectId = "",
    [string]$Region = "asia-southeast1", # Singapore (gần Việt Nam nhất)
    [string]$ServiceName = "aptiskey"
)

Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   🚀 BẮT ĐẦU TRIỂN KHAI APTISKEY LÊN GOOGLE CLOUD RUN" -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan

# 1. Kiểm tra gcloud CLI
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Lỗi: Chưa tìm thấy Google Cloud SDK (gcloud CLI)." -ForegroundColor Red
    Write-Host "Vui lòng cài đặt tại: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# 2. Yêu cầu nhập Project ID nếu chưa có
if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    $currentProject = gcloud config get-value project 2>$null
    if (-not [string]::IsNullOrWhiteSpace($currentProject) -and $currentProject -ne "(unset)") {
        $confirm = Read-Host "Sử dụng GCP Project hiện tại: [$currentProject]? (y/n)"
        if ($confirm -eq "y" -or $confirm -eq "Y" -or $confirm -eq "") {
            $ProjectId = $currentProject
        }
    }
}

if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    $ProjectId = Read-Host "Nhập Google Cloud Project ID của bạn"
}

if ([string]::IsNullOrWhiteSpace($ProjectId)) {
    Write-Host "❌ Project ID không được để trống!" -ForegroundColor Red
    exit 1
}

# 3. Thiết lập Project
Write-Host "📌 Cấu hình dự án: $ProjectId..." -ForegroundColor Green
gcloud config set project $ProjectId

# 4. Kích hoạt các API cần thiết
Write-Host "⚙️ Đang kích hoạt các GCP APIs (Cloud Run, Artifact Registry, Cloud Build)..." -ForegroundColor Green
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# 5. Build và Push Docker Image lên Google Cloud
$ImageTag = "gcr.io/$ProjectId/${ServiceName}:latest"
Write-Host "🔨 Đang build Docker Container Image bằng Google Cloud Build..." -ForegroundColor Green
gcloud builds submit --tag $ImageTag ..

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Quá trình Build Docker Image thất bại." -ForegroundColor Red
    exit 1
}

# 6. Triển khai lên Cloud Run
Write-Host "🚀 Đang triển khai Image lên Cloud Run Service: $ServiceName ($Region)..." -ForegroundColor Green
gcloud run deploy $ServiceName `
    --image $ImageTag `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8001 `
    --memory 1Gi `
    --cpu 1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "======================================================" -ForegroundColor Green
    Write-Host "   🎉 CHÚC MỪNG! WEBSITE ĐÃ ĐƯỢC TRIỂN KHAI THÀNH CÔNG!" -ForegroundColor Green
    Write-Host "======================================================" -ForegroundColor Green
    $serviceUrl = gcloud run services describe $ServiceName --platform managed --region $Region --format "value(status.url)"
    Write-Host "🌐 Đường dẫn Website của bạn: $serviceUrl" -ForegroundColor Cyan
    Write-Host "💡 Hãy vào GCP Console -> Cloud Run -> Variables để bổ sung GEMINI_API_KEY và DATABASE_URL nhé!" -ForegroundColor Yellow
} else {
    Write-Host "❌ Có lỗi xảy ra trong quá trình triển khai." -ForegroundColor Red
}
