from app import schemas
from fastapi import status

# VOTE /vote
def test_vote_up_for_unvoted_post(authorized_client, test_post_ids):
    """Upvote a post that the user hasn't voted on yet and verify vote count."""
    # Confirm no prior votes
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 0
    # Upvote the post
    payload = {"post_id": test_post_ids[0], "dir": schemas.VoteDir.UP}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("message") == "Successfully added vote"
    # Verify vote count incremented
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 1

def test_vote_down_for_voted_post(authorized_client, test_post_ids):
    """Remove an existing upvote from a post and confirm vote count."""
    # Add initial vote
    payload = {"post_id": test_post_ids[0], "dir": schemas.VoteDir.UP}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_200_OK
    # Confirm vote added
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 1
    # Downvote to remove vote
    payload = {"post_id": test_post_ids[0], "dir": schemas.VoteDir.DOWN}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_200_OK
    assert res.json().get("message") == "Successfully deleted vote"
    # Confirm removal
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 0

def test_vote_up_for_voted_post(authorized_client, test_post_ids, test_user_1):
    """Attempt to upvote a post already voted on by the user should fail."""
    # First upvote
    payload = {"post_id": test_post_ids[0], "dir": schemas.VoteDir.UP}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_200_OK
    # Confirm vote added
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 1
    # Attempt duplicate upvote
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_409_CONFLICT
    assert res.json().get("detail") == (
        f"User {test_user_1['id']} has already voted on post {test_post_ids[0]}"
    )

def test_vote_down_for_unvoted_post(authorized_client, test_post_ids):
    """Attempt to remove a vote from a post not voted on should fail."""
    # Confirm no prior votes
    res = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert schemas.PostOut(**res.json()).votes == 0
    # Attempt to downvote
    payload = {"post_id": test_post_ids[0], "dir": schemas.VoteDir.DOWN}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json().get("detail") == "Vote does not exist"

def test_vote_for_post_not_exist(authorized_client):
    """Voting on a non-existent post returns 404."""
    payload = {"post_id": 88888, "dir": schemas.VoteDir.UP}
    res = authorized_client.post("/vote/", json=payload)
    assert res.status_code == status.HTTP_404_NOT_FOUND
    assert res.json().get("detail") == f"Post with id: 88888 does not exist"