from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String
from sqlalchemy.orm import relationship
from neos_core.database.config import Base
from datetime import datetime


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    point_of_sale_id = Column(Integer, ForeignKey("points_of_sale.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    exchange_rate = Column(Numeric(10, 4), nullable=True)
    invoice_type = Column(String(50), nullable=True)
    cae = Column(String(50), nullable=True)
    cae_expiration = Column(DateTime, nullable=True)
    invoice_number = Column(String(50), nullable=True)

    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)
    total = Column(Numeric(10, 2), nullable=False, default=0)

    payment_method = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False, default="completed")

    created_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "SaleDetail",
        back_populates="sale",
        cascade="all, delete-orphan"
    )


class SaleDetail(Base):
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(Numeric(10, 4), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)

    subtotal = Column(Numeric(10, 2), nullable=False)
    tax_amount = Column(Numeric(10, 2), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")
