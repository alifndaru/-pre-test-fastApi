import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, UTC

async def create_user_and_get_token(client: AsyncClient, email: str, password: str = "password"):
    # Register user
    await client.post("/auth/register", json={"email": email, "password": password})
    
    # Login and get token
    response = await client.post("/auth/login", json={"email": email, "password": password})
    return response.json()["access_token"]

@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    token = await create_user_and_get_token(client, "task@example.com")
    
    response = await client.post(
        "/tasks/",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": (datetime.now(UTC) + timedelta(days=1)).isoformat()
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["is_completed"] == False

@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient):
    token = await create_user_and_get_token(client, "get_tasks@example.com")
    
    # Create a task first
    await client.post(
        "/tasks/",
        json={"title": "Test Task 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Get tasks
    response = await client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Test Task 1"

@pytest.mark.asyncio
async def test_update_task(client: AsyncClient):
    token = await create_user_and_get_token(client, "update@example.com")
    
    # Create a task
    create_response = await client.post(
        "/tasks/",
        json={"title": "Original Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Update the task
    response = await client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated Title", "is_completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_completed"] == True

@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    token = await create_user_and_get_token(client, "delete@example.com")
    
    # Create a task
    create_response = await client.post(
        "/tasks/",
        json={"title": "To Delete"},
        headers={"Authorization": f"Bearer {token}"}
    )
    task_id = create_response.json()["id"]
    
    # Delete the task
    response = await client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_cannot_access_other_user_task(client: AsyncClient):
    # Create two users
    token1 = await create_user_and_get_token(client, "user1@example.com")
    token2 = await create_user_and_get_token(client, "user2@example.com")
    
    # User 1 creates a task
    create_response = await client.post(
        "/tasks/",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    task_id = create_response.json()["id"]
    
    # User 2 tries to delete User 1's task
    response = await client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_filter_tasks_by_completion(client: AsyncClient):
    token = await create_user_and_get_token(client, "filter@example.com")
    
    # Create two tasks
    task1_response = await client.post(
        "/tasks/",
        json={"title": "Task 1"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    await client.post(
        "/tasks/",
        json={"title": "Task 2"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Mark first task as completed
    task1_id = task1_response.json()["id"]
    await client.patch(
        f"/tasks/{task1_id}",
        json={"is_completed": True},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Filter completed tasks
    response = await client.get(
        "/tasks/?is_completed=true",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["is_completed"] == True

@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/tasks/")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_update_nonexistent_task(client: AsyncClient):
    token = await create_user_and_get_token(client, "nonexistent@example.com")
    
    # Try to update a task that doesn't exist
    response = await client.patch(
        "/tasks/99999",
        json={"title": "Updated Title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_task(client: AsyncClient):
    token = await create_user_and_get_token(client, "deletenonexistent@example.com")
    
    # Try to delete a task that doesn't exist
    response = await client.delete(
        "/tasks/99999",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_task_invalid_data(client: AsyncClient):
    token = await create_user_and_get_token(client, "invalid@example.com")
    
    # Try to create task without required title
    response = await client.post(
        "/tasks/",
        json={"description": "Task without title"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422  # Validation error