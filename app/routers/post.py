from .. import schemas, models, oauth2
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func, select

router = APIRouter(prefix="/posts", tags=["posts"])


# @router.get("/")
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), limit: int = 10, search: str = ''):
    #    posts = db.execute(select(models.Post).limit(limit)).scalars().all()

    posts = db.execute(select(models.Post, func.count(models.Vote.post_id).label("votes")) \
                         .outerjoin(models.Vote).group_by(models.Post.id) \
                         .where(models.Post.title.contains(search)).limit(limit)).all()

    return posts


@router.get("/{id}", response_model=schemas.PostResponse)
def get_one_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = select(models.Post, func.count(models.Vote.post_id).label("votes")) \
                         .outerjoin(models.Vote).group_by(models.Post.id).where(models.Post.id == id)
    post = db.execute(post_query).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post_query = select(models.Post).where(models.Post.id == id)
    post = db.execute(post_query).scalars().first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="NOT AUTHORIZED to perform such actions")

    db.delete(post)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    post = db.execute(db.query(models.Post).where(models.Post.id == id)).scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} doesn't exist")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="NOT AUTHORIZED to perform such actions")

    for key, value in updated_post.model_dump().items():
        setattr(post, key, value)

    db.commit()

    db.refresh(post)

    return post
