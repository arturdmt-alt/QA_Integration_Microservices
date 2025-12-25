from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="User Service", version="1.0.0")

# In-memory database
users_db = {
    1: {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "active": True},
    2: {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "active": True},
    3: {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com", "active": False}
}

class User(BaseModel):
    id: int
    name: str
    email: str
    active: bool = True

class UserCreate(BaseModel):
    name: str
    email: str
    active: bool = True

@app.get("/")
def read_root():
    return {"service": "User Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Get user by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.get("/users")
def get_all_users(active: Optional[bool] = None):
    """Get all users, optionally filter by active status"""
    if active is None:
        return list(users_db.values())
    return [user for user in users_db.values() if user["active"] == active]

@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    """Create a new user"""
    new_id = max(users_db.keys()) + 1 if users_db else 1
    new_user = {
        "id": new_id,
        "name": user.name,
        "email": user.email,
        "active": user.active
    }
    users_db[new_id] = new_user
    return new_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    """Delete user by ID"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    deleted_user = users_db.pop(user_id)
    return {"message": "User deleted", "user": deleted_user}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    