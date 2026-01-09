from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from neos_core.database.config import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)

    # Relaciones Fiscales
    tax_id_type_id = Column(Integer, ForeignKey("tax_id_types.id"), nullable=False)
    tax_id = Column(String, nullable=False, index=True)  # El número

    tax_responsibility_id = Column(Integer, ForeignKey("tax_responsibilities.id"), nullable=False)

    email = Column(String, nullable=True)
    address = Column(String, nullable=True)

    # Relaciones de ORM
    tax_type = relationship("TaxIdType")
    responsibility = relationship("TaxResponsibility")
    sales = relationship("Sale", back_populates="client")