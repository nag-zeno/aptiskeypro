"""
Router thanh toán VIP qua PayOS (VietQR).
Luồng hoạt động:
1. Frontend gọi POST /api/payment/create → Backend tạo đơn hàng PayOS → Trả về payment_url và QR
2. Người dùng quét mã QR chuyển khoản
3. PayOS gọi Webhook POST /api/payment/webhook → Backend kích hoạt VIP ngay lập tức
"""
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.payment import Transaction, TransactionStatus

router = APIRouter(prefix="/api/payment", tags=["Payment"])


def _generate_order_id(user_id: int) -> str:
    """Tạo order ID unique dựa trên user_id, timestamp và random padding."""
    import time, random
    # PayOS order ID phải là số nguyên, tối đa 9 chữ số
    rand_pad = random.randint(10, 99)
    timestamp = int(time.time()) % 10000
    order_code = f"{user_id % 1000}{timestamp}{rand_pad}"
    return order_code[:9]



@router.post("/create")
async def create_payment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Tạo đơn hàng thanh toán VIP qua PayOS, trả về mã QR và link thanh toán."""
    if not settings.PAYOS_API_KEY or "THAY_THE_" in settings.PAYOS_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Cổng thanh toán chưa được cấu hình. Vui lòng liên hệ admin.",
        )

    order_id_str = _generate_order_id(current_user.id)

    # Lưu transaction tạm thời
    transaction = Transaction(
        user_id=current_user.id,
        amount_vnd=settings.VIP_PRICE_VND,
        duration_days=settings.VIP_DURATION_DAYS,
        payos_order_id=order_id_str,
        status=TransactionStatus.pending,
    )
    db.add(transaction)
    db.commit()

    # Gọi PayOS API
    payload = {
        "orderCode": int(order_id_str),
        "amount": settings.VIP_PRICE_VND,
        "description": f"AptisPro VIP {settings.VIP_DURATION_DAYS} ngay",
        "returnUrl": f"{settings.FRONTEND_URL}/payment/success",
        "cancelUrl": f"{settings.FRONTEND_URL}/payment/cancel",
        "buyerName": current_user.full_name,
        "buyerEmail": current_user.email,
    }

    # Tạo signature cho PayOS
    data_str = (
        f"amount={payload['amount']}&cancelUrl={payload['cancelUrl']}"
        f"&description={payload['description']}&orderCode={payload['orderCode']}"
        f"&returnUrl={payload['returnUrl']}"
    )
    signature = hmac.new(
        settings.PAYOS_CHECKSUM_KEY.encode(),
        data_str.encode(),
        hashlib.sha256,
    ).hexdigest()
    payload["signature"] = signature

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api-merchant.payos.vn/v2/payment-requests",
            json=payload,
            headers={
                "x-client-id": settings.PAYOS_CLIENT_ID,
                "x-api-key": settings.PAYOS_API_KEY,
            },
        )

    if response.status_code != 200:
        try:
            err_data = response.json()
            err_msg = err_data.get("desc") or err_data.get("message") or "Không thể kết nối cổng thanh toán"
        except Exception:
            err_msg = f"Không thể kết nối cổng thanh toán (HTTP {response.status_code})"
        raise HTTPException(status_code=502, detail=err_msg)

    data = response.json()
    if not data or "data" not in data or not data["data"]:
        err_msg = data.get("desc") or data.get("message") or "Lỗi phản hồi dữ liệu từ cổng thanh toán"
        raise HTTPException(status_code=502, detail=err_msg)

    return {
        "order_id": order_id_str,
        "payment_url": data["data"]["checkoutUrl"],
        "qr_code": data["data"]["qrCode"],
        "amount_vnd": settings.VIP_PRICE_VND,
        "duration_days": settings.VIP_DURATION_DAYS,
    }


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Webhook nhận callback từ PayOS khi thanh toán thành công.
    Tự động kích hoạt VIP cho người dùng ngay lập tức.
    """
    body = await request.body()
    data = json.loads(body)

    # Xác thực chữ ký từ PayOS để đảm bảo webhook hợp lệ
    received_signature = data.get("signature", "")
    webhook_data = data.get("data", {})

    check_str = (
        f"amount={webhook_data.get('amount')}&apptransid={webhook_data.get('apptransid','')}"
        f"&bankaccount={webhook_data.get('bankaccount','')}&description={webhook_data.get('description','')}"
        f"&orderCode={webhook_data.get('orderCode','')}&reference={webhook_data.get('reference','')}"
        f"&transactionDateTime={webhook_data.get('transactionDateTime','')}"
    )
    expected_signature = hmac.new(
        settings.PAYOS_CHECKSUM_KEY.encode(),
        check_str.encode(),
        hashlib.sha256,
    ).hexdigest()

    if received_signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    # Tìm transaction và kích hoạt VIP
    order_code = str(webhook_data.get("orderCode", ""))
    transaction = db.query(Transaction).filter(
        Transaction.payos_order_id == order_code,
        Transaction.status == TransactionStatus.pending,
    ).first()

    if not transaction:
        return {"message": "Transaction already processed or not found"}

    # Kích hoạt VIP
    from app.core.security import is_vip_active
    now = datetime.now(timezone.utc)
    user = db.query(User).filter(User.id == transaction.user_id).first()
    if user:
        if is_vip_active(user):
            # Gia hạn từ ngày hết hạn hiện tại
            current_expiry = user.vip_expires_at
            if isinstance(current_expiry, str):
                try:
                    current_expiry = datetime.fromisoformat(current_expiry.replace("Z", "+00:00"))
                except Exception:
                    current_expiry = now
            if current_expiry.tzinfo is None:
                current_expiry = current_expiry.replace(tzinfo=timezone.utc)
            user.vip_expires_at = current_expiry + timedelta(days=transaction.duration_days)
        else:
            # Kích hoạt mới từ hôm nay
            user.vip_expires_at = now + timedelta(days=transaction.duration_days)


        transaction.status = TransactionStatus.completed
        transaction.reference_code = webhook_data.get("reference", "")
        transaction.activated_at = now

        db.commit()

    return {"message": "VIP activated successfully"}
