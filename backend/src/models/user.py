import enum
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, Integer, String, UniqueConstraint, func
from src.core.database import Base


class DocumentType(str, enum.Enum):
    CEDULA = "CEDULA"
    PASAPORTE = "PASAPORTE"


class UserRole(str, enum.Enum):
    ADMIN_GENERAL = "ADMIN_GENERAL"
    ADMIN_COOPERATIVA = "ADMIN_COOPERATIVA"
    SECRETARIA = "SECRETARIA"
    PASAJERO = "PASAJERO"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    document_type = Column(
        SQLEnum(DocumentType, name="document_type_enum"),
        nullable=False,
    )
    document_number = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(
        SQLEnum(UserRole, name="user_role_enum"),
        nullable=False,
        default=UserRole.PASAJERO,
    )
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

    __table_args__ = (
        UniqueConstraint(
            "document_type",
            "document_number",
            name="uq_user_document",
        ),
    )
