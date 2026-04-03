"""对 Item 表的增删改查（只操作数据库，不写 HTTP）。"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def create_item(db: Session, obj: schemas.ItemCreate) -> models.Item:
    row = models.Item(title=obj.title, description=obj.description)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_item(db: Session, item_id: int) -> Optional[models.Item]:
    return db.query(models.Item).filter(models.Item.id == item_id).first()


def list_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Item]:
    return (
        db.query(models.Item)
        .order_by(models.Item.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_item(
    db: Session, item_id: int, obj: schemas.ItemUpdate
) -> Optional[models.Item]:
    row = get_item(db, item_id)
    if row is None:
        return None
    for key, value in obj.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return row


def delete_item(db: Session, item_id: int) -> bool:
    row = get_item(db, item_id)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
