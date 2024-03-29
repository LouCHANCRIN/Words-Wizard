from typing import List, Union, Optional
import datetime

from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(UserLogin):
    email: EmailStr
    

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: str
    created_at: datetime.datetime

    class Config:
        orm_mode = True


class CreateWordsResponse(BaseModel):
    words_inserted: int


class WordResponse(BaseModel):
    character: str
    pinyin: str
    meaning: str
    show_translation: bool

class PostBase(BaseModel):
    title: str
    content: str
    
        
class PostResponse(PostBase):
    published: bool
    created_at: datetime.datetime
    owner_id: int
    
    owner: UserResponse

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    

class TokenData(BaseModel):
    id: Optional[str] = None