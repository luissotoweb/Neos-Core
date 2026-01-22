from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from neos_core.database.config import Base


class AccountingMove(Base):
    __tablename__ = "accounting_moves"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=True, index=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    description = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="draft", index=True)
    move_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    period_year = Column(Integer, nullable=False, index=True)
    period_month = Column(Integer, nullable=False, index=True)
    posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    lines = relationship(
        "AccountingLine",
        back_populates="move",
        cascade="all, delete-orphan"
    )


class AccountingLine(Base):
    __tablename__ = "accounting_lines"

    id = Column(Integer, primary_key=True, index=True)
    move_id = Column(Integer, ForeignKey("accounting_moves.id"), nullable=False, index=True)

    account_code = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    debit = Column(Numeric(12, 2), nullable=False, default=0)
    credit = Column(Numeric(12, 2), nullable=False, default=0)

    move = relationship("AccountingMove", back_populates="lines")
