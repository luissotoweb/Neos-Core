# neos_core/schemas/token_schema.py
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """Estructura de la respuesta al autenticarse exitosamente."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Datos que extraemos del JWT una vez validado."""
    email: Optional[str] = None
    tenant_id: Optional[int] = None
    role: Optional[str] = None