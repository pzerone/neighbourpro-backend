"""
Title: Users router
File: /routers/users.py
Description: This file contains the FastAPI router for user views.
Author: github.com/pzerone
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database.models import Users, UserIn_Pydantic
from tortoise.expressions import Q
import re
from dependencies import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    Token,
    TokenData,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token", scheme_name="JWT")

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    # responses={404: {"description": "Not found"}},
)


@router.post("/register")
async def create_user(user: UserIn_Pydantic):
    user_exists = await Users.filter(Q(username=user.username) | Q(email=user.email))
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")

    if re.match(r"^[^@]+@[^@]+\.[^@]+$", user.email) is None:
        raise HTTPException(status_code=400, detail="Invalid email")

    user.password_hash = get_hashed_password(user.password_hash)
    await Users.create(**user.dict(exclude_unset=True))
    return JSONResponse(content={"detail": "User creation sucessful"}, status_code=201)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    create_user = decode_token(token)
    if create_user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return TokenData(**create_user)


@router.post("/token", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await Users.get(username=form_data.username)
    except:
        return JSONResponse(
            content={"detail": "Invalid username of password"}, status_code=401
        )

    if not verify_password(form_data.password, user.password_hash):
        return JSONResponse(
            content={"detail": "Invalid username of password"}, status_code=401
        )

    token_data = TokenData(username=user.username, email=user.email)
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
    )

@router.get("/me")
async def get_user(user: TokenData = Depends(get_current_user)):
    return user


@router.put("/passwd")
async def change_password(user: TokenData = Depends(get_current_user), old_password: str = None, new_password: str = None):
    if old_password is None:
        raise HTTPException(status_code=400, detail="Old password not provided")
    
    curr_user = await Users.get(username=user.username).only("password_hash")
    old_hash = curr_user.password_hash
    if not verify_password(old_password, old_hash):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    
    if new_password is None:
        raise HTTPException(status_code=400, detail="New password not provided")
    
    new_password = get_hashed_password(new_password)
    await Users.filter(username=user.username).update(password_hash=new_password)
    return JSONResponse(content={"detail": "Password changed successfully"}, status_code=200)