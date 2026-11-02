import sqlite3

from fastapi import APIRouter, Depends, status

from app.controllers import auth_controller
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    return auth_controller.register(db, data)


@router.post("/login", response_model=UserOut, status_code=status.HTTP_200_OK)
def login(data: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    return auth_controller.login(db, data)