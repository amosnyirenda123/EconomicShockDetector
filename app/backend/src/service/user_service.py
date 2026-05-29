import hashlib
import logging

from fastapi import HTTPException

from repository.user_repo import UserRepository
from schemas.schemas import RegisterReq, LoginReq, UserOut, ChatHistoryOut

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash. Replace with bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, req: RegisterReq) -> UserOut:
        existing = self.repository.get_by_email(req.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")

        user = self.repository.create(
            firstname=req.firstname,
            lastname=req.lastname,
            email=req.email,
            hashed_password=_hash_password(req.password),
            date_of_birth=req.date_of_birth,
        )
        logger.info(f"New user registered: {user.email}")
        return UserOut.model_validate(user)

    def login(self, req: LoginReq) -> UserOut:
        user = self.repository.get_by_email(req.email)
        if not user or user.password != _hash_password(req.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        return UserOut.model_validate(user)

    def get_chat_histories(self, user_id: int) -> list[ChatHistoryOut]:
        histories = self.repository.get_chat_histories(user_id)
        return [ChatHistoryOut.model_validate(h) for h in histories]

    def save_chat_entry(self, user_id: int, **kwargs) -> ChatHistoryOut:
        entry = self.repository.save_chat_history(user_id=user_id, **kwargs)
        return ChatHistoryOut.model_validate(entry)