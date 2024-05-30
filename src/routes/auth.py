from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.datebase.db import get_db
from src.datebase.models import Users
from src.schemas import User, UserBase, CreateUser
from src.repository import auth as repository_auth


hash_handler = repository_auth.Hash()
security = HTTPBearer()

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/signup', response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def signup(body: CreateUser, db: Session = Depends(get_db)):
    exist_user = db.query(Users).filter(Users.username == body.username).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exist')
    new_user = Users(username=body.username, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post('/login')
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == body.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username')
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
    
    access_token = await repository_auth.create_access_token(data={'sub': user.username})
    refresh_token = await repository_auth.create_refresh_token(data={'sub': user.username})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    username = await repository_auth.get_username_from_refresh_token(token)
    user = db.query(Users).filter(Users.username == username).first()
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await repository_auth.create_access_token(data={"sub": username})
    refresh_token = await repository_auth.create_refresh_token(data={"sub": username})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

