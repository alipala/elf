from fastapi import FastAPI
from .api import conversations, knowledge
from .database import engine, Base

app = FastAPI(title="Digital Tutor API")

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(conversations.router, prefix="/api")
app.include_router(knowledge.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Digital Tutor API"}