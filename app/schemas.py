from datetime import datetime
from enum import Enum, IntEnum
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

# User Schemas
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    email: EmailStr
    password: str

class UserLogin(UserCreate):
    """Schema for user login (same as creation)."""
    pass

class UserOut(BaseModel):
    """Schema for returning user data (without password)."""
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Post Schemas
class PostBase(BaseModel):
    """Shared properties for Post creation and update."""
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    """Schema for creating a post (inherits PostBase)."""
    pass

class Post(PostBase):
    """Schema representing a Post with metadata and owner."""
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    model_config = ConfigDict(from_attributes=True)

class PostOut(BaseModel):
    """Schema for returning Post data along with vote count."""
    Post: Post
    votes: int

    model_config = ConfigDict(from_attributes=True)

# Authentication Schemas
class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for JWT payload data extracted from token."""
    id: Optional[str] = None

# Vote Schemas
class VoteDir(IntEnum):
    """
    Schema for vote direction.
    Direction of vote: 0 for down, 1 for up.
    """
    DOWN = 0
    UP = 1

class Vote(BaseModel):
    """Schema for vote request."""
    post_id: int
    dir: VoteDir

# Health Check Schemas
class DatabaseStatus(str, Enum):
    """Schema for database connectivity status."""
    connected = "connected"
    unreachable = "unreachable"

class HealthStatus(BaseModel):
    """Schema for overall health status of the application."""
    status: str
    uptime_seconds: int
    version: str
    database: DatabaseStatus