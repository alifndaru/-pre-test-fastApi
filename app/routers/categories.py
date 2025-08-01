from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_session
from app.core.dependencies import get_current_user
from app.schemas.user import User
from app.schemas.category import Category, CategoryCreate, CategoryUpdate, CategoryWithTaskCount
from app.schemas.task import Task
from app.crud import category as crud_category
from app.crud import task as crud_task

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new category"""
    # Check if category name already exists for this user
    existing_category = await crud_category.get_category_by_name(db, category_data.name, current_user.id)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    return await crud_category.create_category(db, category_data, current_user.id)

@router.get("/", response_model=List[Category])
async def read_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    with_task_count: bool = Query(False, description="Include task count for each category"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get all categories for the current user"""
    if with_task_count:
        return await crud_category.get_categories_with_task_count(db, current_user.id, skip, limit)
    else:
        return await crud_category.get_categories(db, current_user.id, skip, limit)

@router.get("/{category_id}", response_model=Category)
async def read_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get a specific category"""
    category = await crud_category.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.put("/{category_id}", response_model=Category)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Update a category"""
    # Check if new name already exists for this user (if name is being updated)
    if category_update.name:
        existing_category = await crud_category.get_category_by_name(db, category_update.name, current_user.id)
        if existing_category and existing_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    category = await crud_category.update_category(db, category_id, current_user.id, category_update)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a category (tasks in this category will have their category set to None)"""
    success = await crud_category.delete_category(db, category_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

@router.get("/{category_id}/tasks", response_model=List[Task])
async def read_category_tasks(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Get all tasks in a specific category"""
    # First check if category exists and belongs to user
    category = await crud_category.get_category(db, category_id, current_user.id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return await crud_task.get_tasks_by_category(db, category_id, current_user.id, skip, limit)
