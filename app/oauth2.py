from app import models, schemas
from app.config import settings
from app.database import get_db
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import decode, encode
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

# JWT & OAuth2 configuration
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# OAuth2 scheme for FastAPI dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# JWT token utilities
def create_access_token(data: dict):
    """
    Generate a JWT access token with an expiration time.
    Args:
        data (dict): Data to encode in the JWT payload (e.g., user_id)
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """
    Verify a JWT token and extract the payload.
    Args:
        token (str): JWT token string
        credentials_exception (HTTPException): Exception to raise if token is invalid
    Returns:
        TokenData: Pydantic schema with extracted user ID
    """
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return schemas.TokenData(id=str(user_id))
    except InvalidTokenError:
        raise credentials_exception

# Dependency to get current user
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    FastAPI dependency to retrieve the currently authenticated user.
    Raises:
        HTTPException: If token is invalid or user not found
    Returns:
        User: SQLAlchemy User instance
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if not user:
        credentials_exception.detail = "User not found"
        raise credentials_exception
    return user