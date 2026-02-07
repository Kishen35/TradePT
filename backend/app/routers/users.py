from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.models import users as UserModels
from app.database.schemas import users as UserSchemas
from app.config.db import engine
from app.config.db import get_db
from app.config.deriv import deriv_api, deriv_api_token

router = APIRouter(prefix="/users", tags=["users"])

# Create tables
UserModels.Base.metadata.create_all(bind=engine)

# Register a new user
@router.post("/", response_model=UserSchemas.UserResponse)
def register_user(user: UserSchemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(UserModels.User).filter(UserModels.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered!")

    db_user = UserModels.User(name=user.name, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# List all users
@router.get("/", response_model=list[UserSchemas.UserResponse])
async def list_users(db: Session = Depends(get_db)):
    # await deriv_api.authorize(deriv_api_token)
    # authorize = await deriv_api.balance()
    # authorize = await deriv_api.exchange_rates({"base_currency": 'USD'})
    # authorize = await deriv_api.portfolio()
    # print(authorize)
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