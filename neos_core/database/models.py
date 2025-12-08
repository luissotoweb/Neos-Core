from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
# Importamos la 'Base' que creamos en config.py
from neos_core.database.config import Base


# 1. Modelo Tenant (El Inquilino o Cliente)
class Tenant(Base):
    __tablename__ = "tenants"
    # Columna clave: Primary Key, Integer, auto-incrementable
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Define la relación con los Usuarios. No crea una columna en DB, es solo para SQLAlchemy.
    users = relationship("User", back_populates="tenant")


# 2. Modelo User (El Usuario que pertenece a un Tenant)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    # Clave Foránea (FK): ESTO define la arquitectura Multi-Tenant.
    # user.tenant_id apunta al campo 'id' de la tabla 'tenants'.
    tenant_id = Column(Integer, ForeignKey("tenants.id"))

    # Define la relación con el Tenant.
    tenant = relationship("Tenant", back_populates="users")