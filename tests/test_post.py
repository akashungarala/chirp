from app import schemas
from fastapi import status
import pytest

# GET /posts
def test_get_all_posts(authorized_client, test_post_ids):
    """Authorized user retrieves all posts."""
    response = authorized_client.get("/posts/")
    assert response.status_code == status.HTTP_200_OK
    posts = [schemas.PostOut(**post) for post in response.json()]
    assert len(posts) == len(test_post_ids)

def test_unauthorized_user_get_all_posts(client):
    """Unauthorized user cannot retrieve posts."""
    response = client.get("/posts/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_unauthorized_user_get_one_post(client, test_post_ids):
    """Unauthorized user cannot retrieve a single post."""
    response = client.get(f"/posts/{test_post_ids[0]}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_one_post_not_exist(authorized_client):
    """Returns 404 for non-existent post."""
    response = authorized_client.get("/posts/88888")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_one_post(authorized_client, test_user_1, test_post_ids, test_posts_data):
    """Authorized user retrieves a specific post."""
    response = authorized_client.get(f"/posts/{test_post_ids[0]}")
    assert response.status_code == status.HTTP_200_OK
    post = schemas.PostOut(**response.json())
    assert post.Post.id == test_post_ids[0]
    assert post.Post.title == test_posts_data[0]["title"]
    assert post.Post.content == test_posts_data[0]["content"]
    assert post.Post.published == test_posts_data[0]["published"]
    assert post.Post.owner_id == test_user_1['id']

# POST /posts
@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "awesome new content", True),
        ("favorite pizza", "i love pepperoni", False),
        ("tallest skyscrapers", "wahoo", True),
    ]
)
def test_create_post(authorized_client, test_user_1, title, content, published):
    """Authorized user can create posts with various payloads."""
    payload = {"title": title, "content": content, "published": published}
    response = authorized_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    post = schemas.Post(**response.json())
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.owner_id == test_user_1['id']

def test_create_post_default_published_true(authorized_client, test_user_1):
    """Published defaults to True if not provided."""
    payload = {"title": "arbitrary title", "content": "sample content"}
    response = authorized_client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    post = schemas.Post(**response.json())
    assert post.published is True

def test_unauthorized_user_create_post(client):
    """Unauthorized user cannot create posts."""
    payload = {"title": "title", "content": "content"}
    response = client.post("/posts/", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# DELETE /posts
def test_delete_post_success(authorized_client, test_post_ids):
    """Authorized user can delete their own post."""
    response = authorized_client.delete(f"/posts/{test_post_ids[0]}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_delete_post_non_exist(authorized_client):
    """Returns 404 when deleting a non-existent post."""
    response = authorized_client.delete("/posts/8000000")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_other_user_post(authorized_client, test_post_ids):
    """User cannot delete another user's post."""
    response = authorized_client.delete(f"/posts/{test_post_ids[3]}")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_unauthorized_user_delete_post(client, test_post_ids):
    """Unauthorized user cannot delete posts."""
    response = client.delete(f"/posts/{test_post_ids[0]}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# PUT /posts
def test_update_post(authorized_client, test_post_ids, test_posts_data):
    """Authorized user can update their own post."""
    data = {"title": "updated title", "content": "updated content", "published": True}
    response = authorized_client.put(f"/posts/{test_post_ids[0]}", json=data)
    assert response.status_code == status.HTTP_200_OK
    post = schemas.Post(**response.json())
    assert post.title == data['title']
    assert post.content == data['content']
    assert post.published == data['published']

def test_update_other_user_post(authorized_client, test_post_ids):
    """User cannot update another user's post."""
    data = {"title": "updated title", "content": "updated content", "published": False}
    response = authorized_client.put(f"/posts/{test_post_ids[3]}", json=data)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_unauthorized_user_update_post(client, test_post_ids):
    """Unauthorized user cannot update posts."""
    response = client.put(f"/posts/{test_post_ids[0]}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_post_non_exist(authorized_client):
    """Returns 404 when updating a non-existent post."""
    data = {"title": "updated title", "content": "updated content", "published": False}
    response = authorized_client.put("/posts/8000000", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND