from fastapi import FastAPI
from .api import conversations, knowledge
from .database import engine, Base
from .ai import openai_integration


app = FastAPI(title="Digital Tutor API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(conversations.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

@app.get("/")
async def root():
    """
    Root endpoint. Returns a simple welcome message.
    
    Returns:
        dict: A JSON-serializable dictionary containing a welcome message.
    """
    return {"message": "Welcome to the Digital Tutor API"}

@app.post("/api/conversations/{conversation_id}/chat")
async def chat_with_tutor(
    conversation_id: int,
    message: schemas.MessageCreate,
    db: Session = Depends(get_db)
):
    
    # Get the conversation and its messages
    conversation = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get relevant knowledge items (you might want to implement a more sophisticated retrieval method)
    knowledge_items = db.query(models.KnowledgeItem).limit(5).all()
    
    # Generate tutor response
    tutor_response = await openai_integration.generate_tutor_response(
        message.content,
        conversation.messages,
        knowledge_items
    )

    # Save user message and tutor response
    user_message = models.Message(content=message.content, is_user=True, conversation_id=conversation_id)
    tutor_message = models.Message(content=tutor_response, is_user=False, conversation_id=conversation_id)
    db.add(user_message)
    db.add(tutor_message)
    db.commit()
    
    return {"user_message": user_message, "tutor_response": tutor_message}