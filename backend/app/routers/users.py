from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models import users as UserModels
from app.database.schemas import users as UserSchemas
from app.config.db import engine
from app.config.db import get_db

router = APIRouter(prefix="/users", tags=["users"])

# Create tables
UserModels.Base.metadata.create_all(bind=engine)

@router.post("/", response_model=UserSchemas.UserResponse)
def create_user(user: UserSchemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModels.User).filter(UserModels.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_user = UserModels.User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/", response_model=list[UserSchemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModels.User).all()
