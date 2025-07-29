# FastAPI Todo Manager

A comprehensive task management API built with FastAPI, featuring user authentication, CRUD operations, and background task processing.

## Features

- 🔐 **JWT Authentication** - Register, login with access/refresh tokens
- 📝 **Task Management** - Create, read, update, delete tasks
- 🔍 **Advanced Filtering** - Filter tasks by completion status and due date
- ⏰ **Background Jobs** - Automated reminders for overdue tasks
- 🧪 **Comprehensive Testing** - Full test coverage with pytest

## Tech Stack

- **Backend**: FastAPI (Python 3.12+)
- **Database**: PostgreSQL with async SQLAlchemy
- **Cache/Queue**: Redis
- **Background Jobs**: Celery
- **Testing**: Pytest with asyncio
- **Migration**: Alembic

## Quick Start

### 1. Setup Environment

```bash
# Clone repository
git clone <repository-url>
cd FastApi-Todo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://username:password@localhost/task_manager
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head
```

### 4. Start Services

```bash
# Start the API server
uvicorn app.main:app --reload

# Start background worker for task reminders (in another terminal)
python -m app.workers.task_reminder

# Alternative: Use Celery (optional)
# celery -A app.workers.task_reminder worker --loglevel=info
# celery -A app.workers.task_reminder beat --loglevel=info
```

### 5. Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user

### Tasks
- `POST /tasks/` - Create new task
- `GET /tasks/` - List tasks (with filtering)
- `PATCH /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

## Project Structure

```
FastApi-Todo/
├── app/
│   ├── core/           # Security & dependencies
│   ├── crud/           # Database operations
│   ├── models/         # SQLAlchemy models
│   ├── routers/        # API routes
│   ├── schemas/        # Pydantic schemas
│   ├── workers/        # Background tasks
│   ├── config.py       # Configuration
│   ├── database.py     # Database setup
│   └── main.py         # FastAPI app
├── alembic/            # Database migrations
├── tests/              # Test suite
└── requirements.txt    # Dependencies
```

## Development

### Code Quality
- Type hints throughout the codebase
- Async/await for all I/O operations
- Clean architecture with separation of concerns
- Comprehensive error handling

### Testing
- Unit tests for all endpoints
- Authentication and authorization tests
- Edge case coverage
- Clean test isolation

## License

MIT License
