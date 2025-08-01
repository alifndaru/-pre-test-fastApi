from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import Optional, TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task

class Category(Base):
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # For hex color codes
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="categories")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="category")
