from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from app.schemas.category import Category

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    category_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None

class Task(TaskBase):
    id: int
    is_completed: bool
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[Category] = None
    
    model_config = ConfigDict(from_attributes=True)

class TaskFilter(BaseModel):
    is_completed: Optional[bool] = None
    due_date_from: Optional[datetime] = None
    due_date_to: Optional[datetime] = None
    category_id: Optional[int] = None