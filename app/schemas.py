"""Pydantic 模型：请求/响应 JSON 形状（给 FastAPI 校验与文档；类似 Swift Codable）。"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ItemUpdate(BaseModel):
    """部分更新：只传需要改的字段即可。"""

    title: Optional[str] = None
    description: Optional[str] = None


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    created_at: datetime
