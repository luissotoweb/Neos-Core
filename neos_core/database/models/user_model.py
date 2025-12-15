# neos_core/database/models/user_model.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base  # Importamos la base


# --- MODELO USER (USUARIO) ---
class User(Base):
    """
    Representa a un usuario que pertenece a un Tenant específico.
    Los usuarios se autentican y acceden a los recursos de su tenant.
    """
    __tablename__ = "users"

    # Campos de Datos
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False, doc="Correo electrónico único (usado para login).")
    hashed_password = Column(String, nullable=False, doc="Contraseña del usuario en formato hash (nunca texto plano).")
    full_name = Column(String, nullable=True, doc="Nombre completo del usuario.")

    # Campos de Seguridad y Pertenencia
    is_active = Column(Boolean, default=True, doc="Indica si la cuenta de usuario está activa.")
    is_superuser = Column(Boolean, default=False, doc="Indica si el usuario tiene permisos de administrador global.")

    # Clave Foránea
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False,
                       doc="ID del Tenant al que pertenece este usuario.")

    # Campos de Seguimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación
    # Usamos una cadena para referenciar a 'Tenant' que aún no está importado
    tenant = relationship("Tenant", back_populates="users")