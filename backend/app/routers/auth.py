from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserRegister, TokenResponse, UserPublic, PasswordResetRequest, PasswordReset, ProfileUpdate, PasswordChange
from app.services.email_service import send_reset_password_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """Dang ky tai khoan moi."""
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email nay da duoc dang ky. Vui long dang nhap hoac dung email khac.",
        )

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Dang nhap bang email va mat khau, nhan JWT token, dong thoi dat cookie de phuc vu cac trang tinh."""
    user = db.query(User).filter(User.email == form_data.username.lower()).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoac mat khau khong dung",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tai khoan cua ban da bi vo hieu hoa. Vui long lien he admin.",
        )

    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # Dat cookie de phuc vu cac trang tinh khong dung localStorage
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=False  # Dat secure=False cho moi truong dev localhost khong co HTTPS
    )

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserPublic)
def get_me(current_user: User = Depends(get_current_user)):
    """Lay thong tin nguoi dung hien tai tu JWT token."""
    return current_user


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db)):
    """
    Gui email chua link dat lai mat khau (het han sau 15 phut).
    Luon tra ve 200 de tranh lo thong tin email co ton tai trong he thong khong.
    """
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user and user.is_active:
        reset_token = create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
        )
        base_url = str(request.base_url).rstrip("/")
        reset_link = f"{base_url}/frontend/auth.html?token={reset_token}"

        await send_reset_password_email(
            to_email=user.email,
            reset_link=reset_link,
            user_name=user.full_name,
        )

    return {"message": "Neu email ton tai trong he thong, ban se nhan duoc huong dan dat lai mat khau trong vai phut."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    """
    Dat lai mat khau moi bang reset token nhan tu email.
    Token phai co claim type=password_reset va chua het han.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Link dat lai mat khau khong hop le hoac da het han. Vui long yeu cau lai.",
    )

    try:
        payload_data = jwt.decode(
            payload.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload_data.get("type") != "password_reset":
            raise credentials_exception

        user_id: str = payload_data.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise credentials_exception

    user.password_hash = get_password_hash(payload.new_password)
    db.commit()

    return {"message": "Mat khau da duoc cap nhat thanh cong! Ban co the dang nhap voi mat khau moi."}


@router.put("/profile", response_model=UserPublic)
def update_profile(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cap nhat thong tin ca nhan (Ho va ten) cua nguoi dung."""
    current_user.full_name = payload.full_name
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Doi mat khau tai khoan dang dang nhap."""
    if not verify_password(payload.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mat khau hien tai khong chinh xac"
        )
    
    if payload.new_password != payload.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mat khau moi va mat khau xac nhan khong khop"
        )
        
    current_user.password_hash = get_password_hash(payload.new_password)
    db.commit()
    return {"message": "Doi mat khau thanh cong!"}

