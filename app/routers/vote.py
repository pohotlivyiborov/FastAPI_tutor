from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session
from .. import oauth2, models, schemas, database


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.execute(select(models.Post).where(models.Post.id == vote.post_id))


    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} doesn't exist")

    found_vote = db.execute(select(models.Vote).
                            where(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)).\
                            scalars().first()

    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"user {current_user.id} has already voted on post number {vote.post_id}")

        new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {'message': 'successfully added the vote'}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="vote doesn't exist")

        db.delete(found_vote)
        db.commit()

        return {'message': 'successfully deleted vote'}