# neos_core/database/models/user_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    # --- CAMBIO IMPORTANTE: Usar role_id en lugar de is_superuser ---
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role", back_populates="users") # <--- Conexión con Role