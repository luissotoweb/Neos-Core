"""
Modelo de cierre de caja (cash count) por Punto de Venta y fecha.
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from neos_core.database.config import Base


class CashCount(Base):
    __tablename__ = "cash_counts"
    __table_args__ = (
        UniqueConstraint("tenant_id", "point_of_sale_id", "count_date", name="uq_cash_count_pos_date"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    point_of_sale_id = Column(Integer, ForeignKey("points_of_sale.id"), nullable=False, index=True)
    count_date = Column(Date, nullable=False, index=True)

    counted_amount = Column(Numeric(10, 2), nullable=False)
    recorded_amount = Column(Numeric(10, 2), nullable=False)
    difference = Column(Numeric(10, 2), nullable=False)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    point_of_sale = relationship("PointOfSale")
    tenant = relationship("Tenant")

    def __repr__(self):
        return (
            f"<CashCount(id={self.id}, pos_id={self.point_of_sale_id}, "
            f"date={self.count_date})>"
        )
