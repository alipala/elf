from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/knowledge/", response_model=schemas.KnowledgeItem)
def create_knowledge_item(item: schemas.KnowledgeItemCreate, db: Session = Depends(get_db)):
    db_item = models.KnowledgeItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/knowledge/", response_model=List[schemas.KnowledgeItem])
def read_knowledge_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(models.KnowledgeItem).offset(skip).limit(limit).all()
    return items