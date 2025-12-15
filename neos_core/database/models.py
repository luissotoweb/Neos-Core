from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from neos_core.database.config import Base


# --- MODELO TENANT (CLIENTE) ---
class Tenant(Base):
    """
    Representa a un cliente o inquilino principal en la arquitectura multi-tenant.
    Cada tenant tiene su propio conjunto de datos lógicamente separados.
    """
    __tablename__ = "tenants"

    # Campos de Datos
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False, doc="Nombre único del cliente o inquilino.")
    description = Column(Text, nullable=True, doc="Descripción detallada del cliente o su rubro.")
    is_active = Column(Boolean, default=True, doc="Indica si el tenant está activo y puede acceder al sistema.")

    # Campos de Seguimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                        doc="Fecha y hora de creación del registro.")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(),
                        doc="Última fecha y hora de actualización del registro.")

    # Relación (Define qué otras tablas están vinculadas a este tenant)
    # Lazy='dynamic' permite cargar los usuarios solo cuando se solicitan explícitamente.
    users = relationship("User", back_populates="tenant", lazy="dynamic")


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
    is_superuser = Column(Boolean, default=False,
                          doc="Indica si el usuario tiene permisos de administrador global (solo para Neos Core).")

    # Clave Foránea (Relación N:1)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False,
                       doc="ID del Tenant al que pertenece este usuario.")

    # Campos de Seguimiento
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relación (Define a qué Tenant pertenece este usuario)
    tenant = relationship("Tenant", back_populates="users")