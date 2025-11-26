from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=['Posts'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Create a new post owned by the current user.
    Args:
        post (schemas.PostCreate): The post data to create.
        db (Session): SQLAlchemy session provided by dependency injection.
        current_user (int): The currently authenticated user.
    Returns:
        schemas.Post: The created post.
    """
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    _ = Depends(get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = ""
):
    """
    Retrieve all posts with optional search, pagination, and vote count.
    Args:
        db (Session): SQLAlchemy session provided by dependency injection.
        _ : Current authenticated user (not used in this function).
        limit (int): Maximum number of posts to return.
        skip (int): Number of posts to skip for pagination.
        search (str): Search term to filter posts by title.
    Returns:
        List[schemas.PostOut]: List of posts with their vote counts.
    """
    posts = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts

@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), _ = Depends(get_current_user)):
    """
    Retrieve a single post by ID, including vote count.
    Args:
        id (int): The ID of the post to retrieve.
        db (Session): SQLAlchemy session provided by dependency injection.
        _ : Current authenticated user (not used in this function).
    Raises:
        HTTPException: 404 Not Found if the post does not exist.
    Returns:
        schemas.PostOut: The requested post with its vote count.
    """
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} was not found"
        )
    return post

@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Update a post by ID. Only the owner can update.
    Args:
        id (int): The ID of the post to update.
        updated_post (schemas.PostCreate): The updated post data.
        db (Session): SQLAlchemy session provided by dependency injection.
        current_user (int): The currently authenticated user.
    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 403 Forbidden if the user is not the owner of the post.
    Returns:
        schemas.Post: The updated post.
    """
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    post_query.update(updated_post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Delete a post by ID. Only the owner can delete.
    Args:
        id (int): The ID of the post to delete.
        db (Session): SQLAlchemy session provided by dependency injection.
        current_user (int): The currently authenticated user.
    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 403 Forbidden if the user is not the owner of the post.
    Returns:
        Response: 204 No Content response on successful deletion.
    """
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {id} does not exist"
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action"
        )
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)