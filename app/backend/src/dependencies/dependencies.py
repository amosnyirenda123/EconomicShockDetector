"""
Simple factories used with FastAPI's Depends() for dependency injection.
Each factory creates the repository / service bound to the current DB session.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.sqlalchemy_connect import get_db
from repository.user_repo import UserRepository
from repository.model_repo import ModelRepository
from service.user_service import UserService
from service.model_service import ModelService


# Repository factories 

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_model_repository(db: Session = Depends(get_db)) -> ModelRepository:
    return ModelRepository(db)


# Service factories 

def get_user_service(
    repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(repo)


def get_model_service(
    repo: ModelRepository = Depends(get_model_repository),
) -> ModelService:
    # ModelService is a singleton-like object (model loaded once at startup).
    # We still inject the repo here so it can persist chat history.
    from service.model_service import _model_service_instance
    _model_service_instance.repository = repo
    return _model_service_instance