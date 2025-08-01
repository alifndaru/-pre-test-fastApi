import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import create_user
from app.schemas.user import UserCreate
from app.core.security import create_access_token


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, db_session: AsyncSession):
    """Test creating a new category"""
    # Create test user
    user_data = UserCreate(email="test@example.com", password="testpassword")
    user = await create_user(db_session, user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create category
    category_data = {
        "name": "Work",
        "description": "Work related tasks",
        "color": "#FF5733"
    }
    
    response = await client.post(
        "/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert data["description"] == "Work related tasks"
    assert data["color"] == "#FF5733"
    assert data["created_by_user_id"] == user.id


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient, db_session: AsyncSession):
    """Test getting all categories"""
    # Create test user
    user_data = UserCreate(email="test2@example.com", password="testpassword")
    user = await create_user(db_session, user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create some categories
    category1_data = {"name": "Personal", "description": "Personal tasks"}
    category2_data = {"name": "Work", "description": "Work tasks"}
    
    await client.post(
        "/categories/",
        json=category1_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    await client.post(
        "/categories/",
        json=category2_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Get categories
    response = await client.get(
        "/categories/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(cat["name"] == "Personal" for cat in data)
    assert any(cat["name"] == "Work" for cat in data)


@pytest.mark.asyncio
async def test_create_task_with_category(client: AsyncClient, db_session: AsyncSession):
    """Test creating a task with a category"""
    # Create test user
    user_data = UserCreate(email="test3@example.com", password="testpassword")
    user = await create_user(db_session, user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create category first
    category_data = {"name": "Work", "description": "Work tasks"}
    category_response = await client.post(
        "/categories/",
        json=category_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    category_id = category_response.json()["id"]
    
    # Create task with category
    task_data = {
        "title": "Complete project",
        "description": "Finish the FastAPI project",
        "category_id": category_id
    }
    
    response = await client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Complete project"
    assert data["category_id"] == category_id
    assert data["category"]["name"] == "Work"


@pytest.mark.asyncio
async def test_get_tasks_by_category_filter(client: AsyncClient, db_session: AsyncSession):
    """Test filtering tasks by category"""
    # Create test user
    user_data = UserCreate(email="test4@example.com", password="testpassword")
    user = await create_user(db_session, user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create categories
    work_category_response = await client.post(
        "/categories/",
        json={"name": "Work", "description": "Work tasks"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    personal_category_response = await client.post(
        "/categories/",
        json={"name": "Personal", "description": "Personal tasks"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    work_category_id = work_category_response.json()["id"]
    personal_category_id = personal_category_response.json()["id"]
    
    # Create tasks with different categories
    await client.post(
        "/tasks/",
        json={"title": "Work task 1", "category_id": work_category_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    await client.post(
        "/tasks/",
        json={"title": "Personal task 1", "category_id": personal_category_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    await client.post(
        "/tasks/",
        json={"title": "Work task 2", "category_id": work_category_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Get tasks filtered by work category
    response = await client.get(
        f"/tasks/?category_id={work_category_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["category"]["name"] == "Work" for task in data)


@pytest.mark.asyncio
async def test_delete_category_sets_tasks_to_none(client: AsyncClient, db_session: AsyncSession):
    """Test that deleting a category sets tasks' category_id to None"""
    # Create test user
    user_data = UserCreate(email="test5@example.com", password="testpassword")
    user = await create_user(db_session, user_data)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.email})
    
    # Create category
    category_response = await client.post(
        "/categories/",
        json={"name": "Temporary", "description": "Temporary category"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    category_id = category_response.json()["id"]
    
    # Create task with category
    task_response = await client.post(
        "/tasks/",
        json={"title": "Task with category", "category_id": category_id},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    task_id = task_response.json()["id"]
    
    # Delete category
    delete_response = await client.delete(
        f"/categories/{category_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert delete_response.status_code == 204
    
    # Check that task's category is now None
    task_get_response = await client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert task_get_response.status_code == 200
    task_data = task_get_response.json()
    assert task_data["category_id"] is None
    assert task_data["category"] is None
