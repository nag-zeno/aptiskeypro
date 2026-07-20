import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey, Float
from app.core.database import Base


class TransactionStatus(str, enum.Enum):
    pending = "pending"       # Chờ thanh toán
    completed = "completed"   # Đã thanh toán thành công
    failed = "failed"         # Thất bại / Hết hạn


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    amount_vnd = Column(Float, nullable=False)
    duration_days = Column(Integer, nullable=False, default=365)

    # PayOS fields
    payos_order_id = Column(String, unique=True, nullable=False, index=True)
    payos_payment_link_id = Column(String, nullable=True)
    reference_code = Column(String, nullable=True)  # Mã giao dịch ngân hàng trả về

    status = Column(SAEnum(TransactionStatus), default=TransactionStatus.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
