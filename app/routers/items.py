"""Item 的 HTTP 接口：增删改查。"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    body: schemas.ItemCreate,
    db: Session = Depends(get_db),
) -> schemas.ItemRead:
    return crud.create_item(db, body)


@router.get("/", response_model=List[schemas.ItemRead])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> List[schemas.ItemRead]:
    return crud.list_items(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)) -> schemas.ItemRead:
    row = crud.get_item(db, item_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@router.patch("/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: int,
    body: schemas.ItemUpdate,
    db: Session = Depends(get_db),
) -> schemas.ItemRead:
    row = crud.update_item(db, item_id, body)
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return row


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)) -> None:
    if not crud.delete_item(db, item_id):
        raise HTTPException(status_code=404, detail="Item not found")
