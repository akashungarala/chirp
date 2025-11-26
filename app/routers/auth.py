from app import models, schemas
from app.database import get_db
from app.oauth2 import create_access_token
from app.utils import verify_password
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate a user and return a JWT access token.
    Args:
        user_credentials (OAuth2PasswordRequestForm): Form containing username (email) and password.
        db (Session): SQLAlchemy session provided by dependency injection.
    Raises:
        HTTPException: 403 Forbidden if credentials are invalid.
    Returns:
        dict: Access token and token type.
    """
    # Retrieve user by email
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    # Verify user existence and password correctness
    if not user or not verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    # Generate JWT access token
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}