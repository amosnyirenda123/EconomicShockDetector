from fastapi import APIRouter, Depends

from dependencies.dependencies import get_user_service
from schemas.schemas import RegisterReq, LoginReq, UserOut, ChatHistoryOut
from service.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=201, summary="Register a new user")
def register(req: RegisterReq, svc: UserService = Depends(get_user_service)):
    return svc.register(req)


@router.post("/login", response_model=UserOut, summary="Login and get user info")
def login(req: LoginReq, svc: UserService = Depends(get_user_service)):
    return svc.login(req)


@router.get("/{user_id}/history", response_model=list[ChatHistoryOut], summary="Get chat history for a user")
def get_history(user_id: int, svc: UserService = Depends(get_user_service)):
    return svc.get_chat_histories(user_id)