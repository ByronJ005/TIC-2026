from typing import Optional
from sqlalchemy.orm import Session
from src.models.user import DocumentType, User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.strip().lower()).first()

    def get_by_document(
        self, document_type: DocumentType, document_number: str
    ) -> Optional[User]:
        return (
            self.db.query(User)
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
