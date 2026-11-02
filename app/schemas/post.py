from typing import List, Optional

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    post_title: str = Field(min_length=1, max_length=200)
    post_body: str = Field(min_length=1)
    post_category: str = Field(min_length=1, max_length=50)


class PostUpdate(BaseModel):
    post_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    post_body: Optional[str] = Field(default=None, min_length=1)
    post_category: Optional[str] = Field(default=None, min_length=1, max_length=50)


class PostOut(BaseModel):
    post_id: int
    post_title: str
    post_body: str
    post_category: str
    created_at: str
    updated_at: str
    user_id: int


class PostPage(BaseModel):
    items: List[PostOut]
    total: int
    page: int
    page_size: int
    total_pages: int
