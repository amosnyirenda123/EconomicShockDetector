from sqlalchemy.orm import Session
from models.sqlalchemy_models import User, ChatHistory


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter(User.id == user_id).first()

    def create(self, firstname: str, lastname: str, email: str,
               hashed_password: str, date_of_birth) -> User:
        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=hashed_password,
            date_of_birth=date_of_birth,
        )
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def get_chat_histories(self, user_id: int) -> list[ChatHistory]:
        return (
            self.session.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .all()
        )

    def save_chat_history(self, user_id: int, **kwargs) -> ChatHistory:
        entry = ChatHistory(user_id=user_id, **kwargs)
        self.session.add(entry)
        self.session.commit()
        self.session.refresh(entry)
        return entry