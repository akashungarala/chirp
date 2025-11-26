from app import models, schemas
from app.database import get_db
from app.utils import get_password_hash
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with a unique email.
    Checks for duplicate email before hashing the password and saving.
    Returns the created user details without the password.
    Args:
        user (schemas.UserCreate): The user data to create.
        db (Session): SQLAlchemy session provided by dependency injection.
    Raises:
        HTTPException: 409 Conflict if email is already registered.
    Returns:
        schemas.UserOut: The created user details.
    """
    # Check if email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    new_user = models.User(**user.model_dump(exclude={"password"}), password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}', response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    """
    Retrieve a user by ID.
    Args:
        id (int): The ID of the user to retrieve.
        db (Session): SQLAlchemy session provided by dependency injection.
    Raises:
        HTTPException: 404 Not Found if the user does not exist.
    Returns:
        schemas.UserOut: The requested user details.
    """
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} does not exist"
        )
    return user