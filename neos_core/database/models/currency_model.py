# neos_core/database/models/currency_model.py
"""
Modelo de Monedas (Global)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from neos_core.database.config import Base


class Currency(Base):
    """
    Representa las monedas disponibles en el sistema.
    Es una tabla global (no tiene tenant_id).
    El SuperAdmin gestiona las monedas del sistema.
    """
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, index=True)

    # Datos de la Moneda
    code = Column(String(10), unique=True, nullable=False, index=True)  # Ej: USD, ARS, MXN
    name = Column(String(50), nullable=False)  # Ej: Dólar Estadounidense
    symbol = Column(String(10), nullable=False)  # Ej: $, US$, €

    # Estado
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Currency(code={self.code}, name={self.name})>"