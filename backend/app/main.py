from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, exam, payment, compat, admin, roadmap, vocabulary

# Tạo tất cả bảng trong database (nếu chưa tồn tại)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AptisPro API",
    description="Backend API cho hệ thống ôn luyện Aptis AptisPro",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,       # Tắt docs khi production
    redoc_url="/redoc" if settings.DEBUG else None,
)

# --- Middleware ---
# allow_origin_regex bao gồm "null" (origin của trang mở từ file://)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_origin_regex=r"null|http://localhost:\d+|http://127\.0\.0\.1:\d+",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(auth.router)
app.include_router(exam.router)
app.include_router(payment.router)
app.include_router(compat.router)
app.include_router(admin.router)
app.include_router(roadmap.router)
app.include_router(vocabulary.router)



@app.get("/health", tags=["System"])
def health_check():
    """Endpoint kiểm tra trạng thái server (dùng cho load balancer / uptime monitor)."""
    return {"status": "ok", "app": settings.APP_NAME}


# --- Phục vụ Giao diện tĩnh (Static Files) ---
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
import os

class PrettyStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404 and not os.path.splitext(path)[1]:
                # Thử tìm file .html tương ứng
                html_path = path + ".html"
                try:
                    return await super().get_response(html_path, scope)
                except HTTPException:
                    pass
            raise ex

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
CRAWLED_DATA_DIR = os.path.join(BACKEND_DIR, "..", "..", "crawled_data")

if os.path.exists(CRAWLED_DATA_DIR):
    # Mount frontend/ (auth.html, ...) tại /frontend
    FRONTEND_DIR = os.path.join(BACKEND_DIR, "..", "..", "frontend")
    if os.path.exists(FRONTEND_DIR):
        app.mount("/frontend", PrettyStaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    # Mount crawled_data/ tại / (trang chủ, các trang tịnh)
    app.mount("/", PrettyStaticFiles(directory=CRAWLED_DATA_DIR, html=True), name="static")
else:
    @app.get("/", tags=["System"])
    def root():
        return {
            "message": f"Chào mừng đến với {settings.APP_NAME} API",
            "docs": "/docs" if settings.DEBUG else "Disabled in production",
            "version": "1.0.0",
        }

