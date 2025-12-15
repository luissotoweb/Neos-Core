from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==========================================================
# 1. ESQUEMAS BASE (Incluyen los campos que se pueden ver)
# ==========================================================

class TenantBase(BaseModel):
    """Esquema base para la creación y lectura de Tenants."""
    # name se convierte en obligatorio (no Optional)
    name: str = Field(..., description="Nombre único del cliente o inquilino.")
    # description es opcional al crearse
    description: Optional[str] = Field(None, description="Descripción detallada del cliente.")


class UserBase(BaseModel):
    """Esquema base para la creación y lectura de Usuarios."""
    email: str = Field(..., description="Correo electrónico del usuario (usado para login).")
    full_name: Optional[str] = Field(None, description="Nombre completo del usuario.")
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


# ==========================================================
# 2. ESQUEMAS DE ENTRADA (Input: Lo que el cliente nos envía)
# ==========================================================

class TenantCreate(TenantBase):
    """
    Schema de ENTRADA para crear un Tenant.
    Hereda de TenantBase, asegurando que solo se necesiten 'name' y 'description'.
    """
    pass  # No necesitamos campos adicionales aquí.


class UserCreate(UserBase):
    """
    Schema de ENTRADA para crear un Usuario.
    Añadimos el campo 'password' que es necesario para crear, pero NUNCA se lee.
    """
    password: str = Field(..., description="Contraseña del usuario (texto plano al crear, NUNCA se almacena).")
    tenant_id: int = Field(..., description="ID del Tenant al que pertenece este usuario.")


# ==========================================================
# 3. ESQUEMAS DE SALIDA (Output: Lo que devolvemos al cliente)
# ==========================================================

class Tenant(TenantBase):
    """
    Schema de SALIDA para un Tenant.
    Incluye campos de DB (id, created_at, etc.) y la relación de usuarios.
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Declaramos la relación para que FastAPI pueda serializarla si es necesario.
    users: List['User'] = []  # Debe ser una lista del propio User schema.

    class Config:
        # Configuración crucial para decirle a Pydantic que trabaje con SQLAlchemy.
        from_attributes = True


class User(UserBase):
    """
    Schema de SALIDA para un Usuario.
    Incluye campos de DB y la relación con el Tenant.
    """
    id: int
    tenant_id: int
    created_at: datetime

    # Omitimos 'hashed_password' por seguridad.

    # Declaramos la relación, pero la hacemos opcional para evitar serializaciones recursivas infinitas.
    tenant: Optional[TenantBase] = None

    class Config:
        # Configuración crucial para decirle a Pydantic que trabaje con SQLAlchemy.
        from_attributes = True


# Esto resuelve el problema de referencia circular (Tenant hace referencia a User y User a Tenant)
Tenant.model_rebuild()