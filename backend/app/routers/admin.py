from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, field_validator

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.exam import Test, UserResult
from app.schemas.user import UserPublic
from app.schemas.exam import ResultDetail
from app.routers.exam import _build_result_detail

router = APIRouter(prefix="/api/admin", tags=["Admin Administration"])


# Dependency đảm bảo chỉ có Admin mới có quyền truy cập
def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập chức năng quản trị này."
        )
    return current_user


# Schema để gia hạn VIP cho học viên
class AdminUpdateVipPayload(BaseModel):
    vip_expires_at: Optional[str] = None  # Định dạng ISO hoặc rỗng để hủy VIP

    @field_validator("vip_expires_at")
    @classmethod
    def validate_date(cls, v):
        if not v:
            return None
        try:
            # Kiểm tra định dạng thời gian gửi lên
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
            return dt
        except ValueError:
            raise ValueError("Định dạng ngày tháng không hợp lệ. Vui lòng gửi định dạng ISO 8601.")


# 1. API: Lấy danh sách tất cả người dùng
@router.get("/users", response_model=List[UserPublic])
def admin_list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Lấy danh sách toàn bộ người dùng trong hệ thống (chỉ dành cho Admin)."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


# 2. API: Cập nhật VIP cho một tài khoản cụ thể
@router.put("/users/{user_id}/vip", response_model=UserPublic)
def admin_update_user_vip(
    user_id: int,
    payload: AdminUpdateVipPayload,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Gia hạn hoặc cập nhật ngày hết hạn VIP cho học viên cụ thể (chỉ dành cho Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy người dùng")
    
    if payload.vip_expires_at is None:
        user.vip_expires_at = None
    else:
        user.vip_expires_at = payload.vip_expires_at

    db.commit()
    db.refresh(user)
    return user


# 3. API: Lấy tất cả lịch sử làm bài thi của toàn hệ thống
@router.get("/results", response_model=List[ResultDetail])
def admin_list_all_results(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Lấy danh sách toàn bộ lịch sử làm đề thi của mọi học viên trong hệ thống (chỉ dành cho Admin)."""
    results = db.query(UserResult).order_by(UserResult.completed_at.desc()).all()
    
    # Map kết quả sang schema ResultDetail
    return [_build_result_detail(r, db) for r in results]


# 4. API: Lấy lịch sử làm bài thi của một học viên cụ thể
@router.get("/users/{user_id}/results", response_model=List[ResultDetail])
def admin_list_user_results(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Lấy danh sách lịch sử làm đề thi của một học viên cụ thể (chỉ dành cho Admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Không tìm thấy học viên")
        
    results = db.query(UserResult).filter(UserResult.user_id == user_id).order_by(UserResult.completed_at.desc()).all()
    return [_build_result_detail(r, db) for r in results]
