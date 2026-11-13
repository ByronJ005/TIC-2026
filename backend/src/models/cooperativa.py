from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship
from src.core.database import Base


class Cooperativa(Base):
    __tablename__ = "cooperatives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    ruc = Column(String(13), unique=True, nullable=False, index=True)
    address = Column(String(150), nullable=True)
    phone = Column(String(10), nullable=True)
    email = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    administradores = relationship(
        "User",
        back_populates="cooperativa",
        foreign_keys="User.cooperativa_id",
        lazy="selectin",
    )

    __table_args__ = (
        Index("uq_cooperatives_lower_name", func.lower(name), unique=True),
        CheckConstraint("length(ruc) = 13", name="ck_cooperatives_ruc_length"),
        CheckConstraint("length(name) >= 1", name="ck_cooperatives_name_min_length"),
    )

