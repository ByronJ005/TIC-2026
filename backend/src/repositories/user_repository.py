from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from src.models.user import DocumentType, User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .options(selectinload(User.role_associations))
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .options(selectinload(User.role_associations))
            .filter(User.email == email.strip().lower())
            .first()
        )

    def get_by_document(
        self, document_type: DocumentType, document_number: str
    ) -> Optional[User]:
        return (
            self.db.query(User)
            .options(selectinload(User.role_associations))
            .filter(
                User.document_type == document_type,
                User.document_number == document_number.strip(),
            )
            .first()
        )

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(
        self,
        search: str = "",
        include_inactive: bool = False,
        offset: int = 0,
        limit: int = 10,
    ) -> Tuple[List[User], int]:
        query = self.db.query(User).options(selectinload(User.role_associations))

        if not include_inactive:
            query = query.filter(User.is_active.is_(True))

        cleaned_search = search.strip()
        if cleaned_search:
            pattern = f"%{cleaned_search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(pattern),
                    User.last_name.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )

        total = query.count()
        users = (
            query.order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return users, total

    def update_roles(self, user: User, roles: List[UserRole]) -> User:
        user.roles = roles
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_profile(self, user: User, fields: Dict[str, Any]) -> User:
        """Applies all given column values in a single transaction."""
        for column_name, value in fields.items():
            setattr(user, column_name, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(
        self, user: User, hashed_password: str, changed_at: datetime
    ) -> User:
        return self.update_profile(
            user,
            {"hashed_password": hashed_password, "password_changed_at": changed_at},
        )

