from fastapi import FastAPI
from src.routers import exercises, users

app = FastAPI(
    title="Progressive Overload Tracker API",
    description="API for tracking workout progress and progressive overload",
    version="1.0.0",
)

# Include routers
app.include_router(exercises.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Progressive Overload Tracker API"}
