import sqlite3
from typing import Literal, Optional

from fastapi import APIRouter, Depends, Query, Response, status

from app.controllers import post_controller
from app.controllers.auth_controller import get_current_user
from app.database import get_db
from app.schemas.post import PostCreate, PostOut, PostPage, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostPage)
def list_posts(
    category: Optional[str] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    sort: Literal["newest", "oldest"] = "newest",
    db: sqlite3.Connection = Depends(get_db),
):
    return post_controller.list_posts(db, category, user_id, search, page, page_size, sort)


@router.get("/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: sqlite3.Connection = Depends(get_db)):
    return post_controller.get_post(db, post_id)


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    data: PostCreate,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    return post_controller.create_post(db, data, current_user["user_id"])


@router.put("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    data: PostUpdate,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    return post_controller.update_post(db, post_id, data, current_user["user_id"])


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: dict = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
):
    post_controller.delete_post(db, post_id, current_user["user_id"])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
