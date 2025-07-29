import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.crud.task import get_overdue_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_overdue_tasks():
    """Check for overdue tasks and log reminders"""
    async with async_session_maker() as session:
        try:
            overdue_tasks = await get_overdue_tasks(session)
            
            if overdue_tasks:
                logger.info(f"Found {len(overdue_tasks)} overdue tasks")
                
                for task in overdue_tasks:
                    # Load user relationship
                    await session.refresh(task, ["owner"])
                    
                    logger.info(
                        f"REMINDER: Task '{task.title}' (ID: {task.id}) "
                        f"for user {task.owner.email} was due on {task.due_date} "
                        f"and is now {datetime.utcnow() - task.due_date} overdue"
                    )
            # Only log when there are overdue tasks (remove noise)
            # else:
            #     logger.info("No overdue tasks found")
                
        except Exception as e:
            logger.error(f"Error checking overdue tasks: {e}")

async def start_background_worker():
    """Start the background worker that runs every 30 seconds"""
    logger.info("Starting background worker for task reminders")
    
    while True:
        try:
            await check_overdue_tasks()
            await asyncio.sleep(30)  # Wait 30 seconds
        except Exception as e:
            logger.error(f"Background worker error: {e}")
            await asyncio.sleep(30)  # Continue running even if there's an error

if __name__ == "__main__":
    asyncio.run(start_background_worker())