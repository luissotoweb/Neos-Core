# neos_core/database/models/role_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from neos_core.database.config import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)  # 'superadmin', 'admin', 'seller', etc.
    description = Column(String)

    # Relación inversa: Un rol puede pertenecer a muchos usuarios
    users = relationship("User", back_populates="role")