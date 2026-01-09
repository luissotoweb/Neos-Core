# neos_core/database/models/sales_model.py
from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String
from sqlalchemy.orm import relationship
from neos_core.database.config import Base
from datetime import datetime


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Vendedor
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)  # Opcional (Venta a Consumidor Final)

    # Datos de la Venta
    total = Column(Float, default=0.0)
    status = Column(String, default="completed")  # completed, cancelled, pending
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    tenant = relationship("Tenant")
    seller = relationship("User")
    client = relationship("Client", back_populates="sales")
    items = relationship("SaleDetail", back_populates="sale", cascade="all, delete-orphan")

    # Datos de Facturación Legal
    pos_id = Column(Integer, ForeignKey("points_of_sale.id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    exchange_rate = Column(Float, default=1.0)  # Valor del dólar/moneda al momento

    # Datos devueltos por ente fiscal (AFIP/SAT/etc)
    invoice_number = Column(Integer, nullable=True)  # El número correlativo
    cae = Column(String, nullable=True)  # Código de Autorización Electrónico
    cae_expiration = Column(DateTime, nullable=True)

    # Relaciones
    pos = relationship("PointOfSale")
    currency = relationship("Currency")


class SaleDetail(Base):
    __tablename__ = "sale_details"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Capturamos datos en el momento de la venta (por si el producto cambia de precio después)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Precio al que se vendió
    tax_rate = Column(Float, default=21.0)  # Ej: IVA 21% o 10.5%

    # Relaciones
    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")