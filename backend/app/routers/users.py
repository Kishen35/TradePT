from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.model import users as UserModels
from app.database.schemas import users as UserSchemas
from app.config.db import engine
from app.config.db import get_db
from sqlalchemy import inspect, text

router = APIRouter(prefix="/users", tags=["users"])

# Create tables
UserModels.Base.metadata.create_all(bind=engine)

# Add trader_type column if it doesn't exist (for existing DBs)
with engine.connect() as conn:
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("users")]
    if "trader_type" not in columns:
        conn.execute(text("ALTER TABLE users ADD COLUMN trader_type VARCHAR"))
        conn.commit()

# Register a new user
@router.post("/", response_model=UserSchemas.UserResponse)
def register_user(user: UserSchemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModels.User).filter(UserModels.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_user = UserModels.User(name=user.name, email=user.email, password=user.password, experience_level=user.experience_level, trading_duration=user.trading_duration, risk_tolerance=user.risk_tolerance, capital_allocation=user.capital_allocation, asset_preference=user.asset_preference)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# List all users
@router.get("/", response_model=list[UserSchemas.UserResponse])
async def list_users(db: Session = Depends(get_db)):
    return db.query(UserModels.User).all()

# Login user (together with Deriv account)
@router.post("/login", response_model=UserSchemas.UserResponse)
async def login_user(credentials: UserSchemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserModels.User).filter(
        UserModels.User.email == credentials.email,
        UserModels.User.password == credentials.password
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password!")
    return user

# Set trader type (momentum or precision) after style profiling
@router.put("/{user_id}/trader-type", response_model=UserSchemas.UserResponse)
def set_trader_type(user_id: int, payload: UserSchemas.TraderTypeUpdate, db: Session = Depends(get_db)):
    user = db.query(UserModels.User).filter(UserModels.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.trader_type = payload.trader_type
    db.commit()
    db.refresh(user)
    return user