from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models.category import Category
from app.models.task import Task
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryWithTaskCount
from typing import List, Optional

async def create_category(db: AsyncSession, category: CategoryCreate, user_id: int) -> Category:
    db_category = Category(**category.model_dump(), created_by_user_id=user_id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def get_category(db: AsyncSession, category_id: int, user_id: int) -> Optional[Category]:
    result = await db.execute(
        select(Category).where(and_(Category.id == category_id, Category.created_by_user_id == user_id))
    )
    return result.scalar_one_or_none()

async def get_categories(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[Category]:
    result = await db.execute(
        select(Category)
        .where(Category.created_by_user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_categories_with_task_count(
    db: AsyncSession, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[CategoryWithTaskCount]:
    # Query categories with task count
    result = await db.execute(
        select(
            Category,
            func.count(Task.id).label('task_count')
        )
        .outerjoin(Task, and_(Task.category_id == Category.id, Task.created_by_user_id == user_id))
        .where(Category.created_by_user_id == user_id)
        .group_by(Category.id)
        .offset(skip)
        .limit(limit)
    )
    
    categories_with_count = []
    for category, task_count in result:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "color": category.color,
            "created_by_user_id": category.created_by_user_id,
            "task_count": task_count or 0
        }
        categories_with_count.append(CategoryWithTaskCount(**category_dict))
    
    return categories_with_count

async def update_category(db: AsyncSession, category_id: int, user_id: int, category_update: CategoryUpdate) -> Optional[Category]:
    db_category = await get_category(db, category_id, user_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> bool:
    db_category = await get_category(db, category_id, user_id)
    if not db_category:
        return False
    
    # Set category_id to None for all tasks in this category
    await db.execute(
        Task.__table__.update()
        .where(and_(Task.category_id == category_id, Task.created_by_user_id == user_id))
        .values(category_id=None)
    )
    
    await db.delete(db_category)
    await db.commit()
    return True

async def get_category_by_name(db: AsyncSession, name: str, user_id: int) -> Optional[Category]:
    result = await db.execute(
        select(Category).where(and_(Category.name == name, Category.created_by_user_id == user_id))
    )
    return result.scalar_one_or_none()