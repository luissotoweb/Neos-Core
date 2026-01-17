# neos_core/database/models/sales_model.py

from sqlalchemy import Column, Integer, ForeignKey, Numeric, DateTime, String, Text
from sqlalchemy.orm import relationship
from neos_core.database.config import Base
from datetime import datetime


class Sale(Base):
    """
    Representa una venta completa.
    Soporta facturación electrónica opcional (CAE).
    """
    __tablename__ = "sales"

    # IDs y Referencias
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Vendedor
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)  # Opcional (Consumidor Final)
    point_of_sale_id = Column(Integer, ForeignKey("points_of_sale.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)

    # Montos (IMPORTANTE: Usar Numeric para dinero, NO Float)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)  # Suma de items sin impuesto
    tax_amount = Column(Numeric(10, 2), nullable=False, default=0)  # Total de impuestos
    total = Column(Numeric(10, 2), nullable=False, default=0)  # subtotal + tax_amount
    exchange_rate = Column(Numeric(10, 4), nullable=False, default=1.0)

    # Método de Pago
    payment_method = Column(String(50), nullable=False)  # CASH, CARD, TRANSFER, etc.

    # Estado de la Venta
    status = Column(String(20), default="completed", nullable=False)  # completed, cancelled, pending

    # Facturación Electrónica (OPCIONAL - Puede ser NULL si no aplica)
    invoice_type = Column(String(10), nullable=True)  # A, B, C (Argentina) o equivalente
    invoice_number = Column(String(50), nullable=True)  # Ej: 00001-00012345
    cae = Column(String(50), nullable=True)  # Código de Autorización Electrónico
    cae_expiration = Column(DateTime, nullable=True)  # Fecha de vencimiento del CAE

    # Observaciones internas
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    tenant = relationship("Tenant")
    seller = relationship("User", foreign_keys=[user_id])
    client = relationship("Client", back_populates="sales")
    items = relationship("SaleDetail", back_populates="sale", cascade="all, delete-orphan")
    point_of_sale = relationship("PointOfSale")
    currency = relationship("Currency")


class SaleDetail(Base):
    """
    Detalle de cada producto vendido en una venta.
    Captura precio y tasa de impuesto en el momento de la venta (histórico).
    """
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Datos capturados en el momento de la venta (no cambian si el producto cambia después)
    quantity = Column(Numeric(10, 4), nullable=False)  # Permite decimales (Ej: 2.5 kg)
    unit_price = Column(Numeric(10, 2), nullable=False)  # Precio unitario sin impuesto
    tax_rate = Column(Numeric(5, 2), nullable=False, default=0)  # Ej: 21.00 para IVA 21%

    # Campos calculados (para facilitar reportes)
    subtotal = Column(Numeric(10, 2), nullable=False)  # quantity * unit_price
    tax_amount = Column(Numeric(10, 2), nullable=False)  # subtotal * (tax_rate / 100)
    total = Column(Numeric(10, 2), nullable=False)  # subtotal + tax_amount

    # Relaciones
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")