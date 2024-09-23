from pydantic import BaseModel
from typing import List, Optional

class MessageBase(BaseModel):
    content: str
    is_user: bool

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    conversation_id: int

    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    pass

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    messages: List[Message] = []

    class Config:
        orm_mode = True

class KnowledgeItemBase(BaseModel):
    content: str

class KnowledgeItemCreate(KnowledgeItemBase):
    pass

class KnowledgeItem(KnowledgeItemBase):
    id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_tutor: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None