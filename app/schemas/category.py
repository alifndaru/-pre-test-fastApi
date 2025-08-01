from pydantic import BaseModel, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None  # Hex color code like #FF5733

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class Category(CategoryBase):
    id: int
    created_by_user_id: int
    
    model_config = ConfigDict(from_attributes=True)

class CategoryWithTaskCount(Category):
    task_count: int = 0
