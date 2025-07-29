from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskFilter
from typing import List, Optional
from datetime import datetime

async def create_task(db: AsyncSession, task: TaskCreate, user_id: int) -> Task:
    db_task = Task(**task.model_dump(), created_by_user_id=user_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def get_task(db: AsyncSession, task_id: int, user_id: int) -> Optional[Task]:
    result = await db.execute(
        select(Task).where(and_(Task.id == task_id, Task.created_by_user_id == user_id))
    )
    return result.scalar_one_or_none()

async def get_tasks(
    db: AsyncSession, 
    user_id: int, 
    filters: TaskFilter,
    skip: int = 0, 
    limit: int = 100
) -> List[Task]:
    query = select(Task).where(Task.created_by_user_id == user_id)
    
    if filters.is_completed is not None:
        query = query.where(Task.is_completed == filters.is_completed)
    
    if filters.due_date_from:
        query = query.where(Task.due_date >= filters.due_date_from)
    
    if filters.due_date_to:
        query = query.where(Task.due_date <= filters.due_date_to)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_task(db: AsyncSession, task_id: int, user_id: int, task_update: TaskUpdate) -> Optional[Task]:
    db_task = await get_task(db, task_id, user_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    await db.commit()
    await db.refresh(db_task)
    return db_task

async def delete_task(db: AsyncSession, task_id: int, user_id: int) -> bool:
    db_task = await get_task(db, task_id, user_id)
    if not db_task:
        return False
    
    await db.delete(db_task)
    await db.commit()
    return True

async def get_overdue_tasks(db: AsyncSession) -> List[Task]:
    now = datetime.utcnow()
    result = await db.execute(
        select(Task).where(
            and_(
                Task.due_date < now,
                Task.is_completed == False
            )
        )
    )
    return result.scalars().all()