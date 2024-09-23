from fastapi import FastAPI
from .api import conversations, knowledge
from .database import engine, Base
from .ai import openai_integration
from .auth import jwt_auth

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

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = jwt_auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt_auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = jwt_auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user