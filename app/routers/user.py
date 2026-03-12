from .. import schemas, utils, models
from fastapi import Depends, HTTPException, status, APIRouter
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = utils.hash(user.password)
    user.password = hashed_pwd

    new_user = models.User(**user.model_dump())
    existing_email = db.execute(select(models.User).where(models.User.email == user.email)).scalars().first()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="пользователь с таким email уже есть в базе"
        )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.execute(select(models.User).where(models.User.id == id)).scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id {id} doesn't exist")
    return user
