from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from app.database import get_async_session
from app.schemas.task import Task, TaskCreate, TaskUpdate, TaskFilter
from app.crud.task import create_task, get_tasks, get_task, update_task, delete_task
from app.core.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_new_task(
    task: TaskCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    return await create_task(db=db, task=task, user_id=current_user.id)

@router.get("/", response_model=List[Task])
async def read_tasks(
    is_completed: Optional[bool] = Query(None),
    due_date_from: Optional[datetime] = Query(None),
    due_date_to: Optional[datetime] = Query(None),
    category_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    filters = TaskFilter(
        is_completed=is_completed,
        due_date_from=due_date_from,
        due_date_to=due_date_to,
        category_id=category_id
    )
    return await get_tasks(db=db, user_id=current_user.id, filters=filters, skip=skip, limit=limit)

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    task = await get_task(db=db, task_id=task_id, user_id=current_user.id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

@router.patch("/{task_id}", response_model=Task)
async def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    updated_task = await update_task(db=db, task_id=task_id, user_id=current_user.id, task_update=task_update)
    if not updated_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return updated_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_task(
    task_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    deleted = await delete_task(db=db, task_id=task_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")