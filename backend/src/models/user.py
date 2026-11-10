import enum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from src.core.database import Base


class DocumentType(str, enum.Enum):
    CEDULA = "CEDULA"
    PASAPORTE = "PASAPORTE"


class UserRole(str, enum.Enum):
    ADMIN_GENERAL = "ADMIN_GENERAL"
    ADMIN_COOPERATIVA = "ADMIN_COOPERATIVA"
    SECRETARIA_COOPERATIVA = "SECRETARIA_COOPERATIVA"
    PASAJERO = "PASAJERO"


class UserRoleAssociation(Base):
    __tablename__ = "user_roles"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = Column(
        SQLEnum(UserRole, name="user_role_enum"),
        primary_key=True,
    )

    user = relationship("User", back_populates="role_associations")

    def __init__(self, role: UserRole = None, **kwargs):
        if role is not None:
            kwargs["role"] = role
        super().__init__(**kwargs)


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

    role_associations = relationship(
        "UserRoleAssociation",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    roles = association_proxy(
        "role_associations",
        "role",
        creator=lambda r: UserRoleAssociation(role=r),
    )

    __table_args__ = (
        UniqueConstraint(
            "document_type",
            "document_number",
            name="uq_user_document",
        ),
    )

