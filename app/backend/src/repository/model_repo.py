from sqlalchemy.orm import Session
from models.sqlalchemy_models import ChatHistory
from sqlalchemy import desc


class ModelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_history_by_id(self, history_id: int) -> ChatHistory | None:
        return self.session.query(ChatHistory).filter(ChatHistory.id == history_id).first()

    def list_all_histories(self, limit: int = 50) -> list[ChatHistory]:
        return (
            self.session.query(ChatHistory)
            .order_by(desc(ChatHistory.created_at))
            .limit(limit)
            .all()
        )