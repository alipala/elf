from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from .. import models, schemas
from ..database import get_db
from ..auth.jwt_auth import get_current_user
from ..ai import openai_integration 

router = APIRouter()

@router.get("/conversations/stats", response_model=dict)
async def get_conversation_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_tutor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    total_conversations = db.query(func.count(models.Conversation.id)).scalar()
    total_messages = db.query(func.count(models.Message.id)).scalar()
    avg_messages_per_conversation = db.query(func.avg(func.count(models.Message.id))).group_by(models.Message.conversation_id).scalar()
    
    return {
        "total_conversations": total_conversations,
        "total_messages": total_messages,
        "avg_messages_per_conversation": float(avg_messages_per_conversation) if avg_messages_per_conversation else 0
    }

@router.get("/knowledge/search", response_model=List[schemas.KnowledgeItem])
async def search_knowledge(query: str, db: Session = Depends(get_db)):
    results = db.query(models.KnowledgeItem).filter(models.KnowledgeItem.content.ilike(f"%{query}%")).all()
    return results

@router.post("/knowledge/bulk", response_model=List[schemas.KnowledgeItem])
async def bulk_add_knowledge(items: List[schemas.KnowledgeItemCreate], db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if not current_user.is_tutor:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_items = [models.KnowledgeItem(**item.dict()) for item in items]
    db.add_all(db_items)
    db.commit()
    for item in db_items:
        db.refresh(item)
    return db_items

@router.get("/conversations/{conversation_id}/summary", response_model=str)
async def get_conversation_summary(conversation_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = [msg.content for msg in conversation.messages]
    summary = await openai_integration.generate_summary(messages)
    return summary