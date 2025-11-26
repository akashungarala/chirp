from app import models, schemas
from app.database import get_db
from app.oauth2 import get_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/vote", tags=['Vote'])

@router.post("/", status_code=status.HTTP_200_OK)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    """
    Upvote or remove a vote for a post.
    - If `dir` is UP, adds a vote if not already voted by the user.
    - If `dir` is DOWN, removes the existing vote.
    Args:
        vote (schemas.Vote): The vote data containing post_id and direction.
        db (Session): SQLAlchemy session provided by dependency injection.
        current_user (int): The ID of the currently authenticated user.
    Raises:
        HTTPException: 404 Not Found if the post does not exist.
        HTTPException: 409 Conflict if trying to upvote again or remove a non-existent vote.
    Returns:
        dict: A message indicating the result of the vote operation.
    """
    # Ensure post exists
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id: {vote.post_id} does not exist"
        )
    # Check if current user has already voted
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id,
        models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if vote.dir == schemas.VoteDir.UP:
        # Prevent duplicate votes
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User {current_user.id} has already voted on post {vote.post_id}"
            )
        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else: # VoteDir.DOWN
        # Ensure a vote exists to remove
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote does not exist"
            )
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "Successfully deleted vote"}