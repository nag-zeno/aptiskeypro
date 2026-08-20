#!/bin/bash
# ==============================================================================
# Script Triển khai AptisKey lên Google Cloud Run (Bash / Cloud Shell)
# ==============================================================================

set -e

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"asia-southeast1"}
SERVICE_NAME=${3:-"aptiskey"}

echo "======================================================"
echo "   🚀 BẮT ĐẦU TRIỂN KHAI APTISKEY LÊN GOOGLE CLOUD RUN"
echo "======================================================"

if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "(unset)" ]; then
    read -p "Nhập Google Cloud Project ID của bạn: " PROJECT_ID
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Lỗi: Project ID không được để trống!"
    exit 1
fi

echo "📌 Cấu hình dự án: $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "⚙️ Kích hoạt các API cần thiết..."
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

IMAGE_TAG="gcr.io/$PROJECT_ID/${SERVICE_NAME}:latest"

echo "🔨 Đang build Docker Container Image bằng Google Cloud Build..."
# Đi lên thư mục gốc dự án nếu đang đứng trong deploy/
if [ -f "Dockerfile" ]; then
    BUILD_DIR="."
elif [ -f "../Dockerfile" ]; then
    BUILD_DIR=".."
else
    echo "❌ Không tìm thấy Dockerfile!"
    exit 1
fi

gcloud builds submit --tag "$IMAGE_TAG" "$BUILD_DIR"

echo "🚀 Đang triển khai lên Cloud Run ($REGION)..."
gcloud run deploy "$SERVICE_NAME" \
    --image "$IMAGE_TAG" \
    --platform managed \
    --region "$REGION" \
    --allow-unauthenticated \
    --port 8001 \
    --memory 1Gi \
    --cpu 1

echo ""
echo "======================================================"
echo "   🎉 TRIỂN KHAI THÀNH CÔNG!"
echo "======================================================"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format "value(status.url)")
echo "🌐 URL Website: $SERVICE_URL"
