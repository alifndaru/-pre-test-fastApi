from fastapi import FastAPI
from app.routers import auth, tasks, categories

app = FastAPI(title="FastAPI Todo", version="1.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(categories.router)

@app.get("/")
async def root():
    return {"message": "FastAPI Todo API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}