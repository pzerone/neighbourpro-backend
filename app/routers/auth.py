"""
Title: Auth router
File: /routers/auth.py
Description: This file contains the FastAPI router for Auth views.
Author: github.com/pzerone
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database.models import Users
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
from tortoise.contrib.pydantic.creator import pydantic_model_creator

signup_data = pydantic_model_creator(
    Users,
    name="User Signup Data Input",
    exclude_readonly=True,
    exclude=(
        "role",
        "profession_id",
        "hourly_rate",
        "worker_bio",
        "House_name",
        "Street",
        "City",
        "State",
        "Pincode",
        "Latitude",
        "Longitude",
    ),
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", scheme_name="JWT")

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/register")
async def create_user(user: signup_data):
    """
    This route is used to create a new user.
    
    requires:
    - username
    - first_name
    - last_name
    - email
    - phone_number
    - password
    
    Password must be atleast 8 characters long and contain atleast one letter and one number
    """
    user_exists = await Users.filter(Q(username=user.username) | Q(email=user.email))
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")

    if re.match(r"^[^@]+@[^@]+\.[^@]+$", user.email) is None:
        raise HTTPException(status_code=400, detail="Invalid email")

    if re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", user.password_hash) is None:
        raise HTTPException(
            status_code=400,
            detail="Password must be atleast 8 characters long and contain atleast one letter and one number",
        )
    user.password_hash = get_hashed_password(user.password_hash)
    await Users.create(**user.dict(exclude_unset=True))
    return JSONResponse(content={"detail": "User creation sucessful"}, status_code=201)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    create_user = decode_token(token)
    if create_user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return TokenData(**create_user)


@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This route is used to login a user.

    requires:
    - username
    - password

    returns:
    - access_token
    - refresh_token
    - token_type
    """
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

    token_data = TokenData(
        username=user.username, email=user.email, role=user.role, id=user.id
    )
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
    )


@router.get("/me")
async def get_user(user: TokenData = Depends(get_current_user)):
    """
    This route is used to get the details of the logged in user.

    returns:
    - id
    - username
    - role
    - email
    """
    return user


@router.put("/ch-passwd")
async def change_password(
    user: TokenData = Depends(get_current_user),
    old_password: str = None,
    new_password: str = None,
):
    """
    This route is used to change the password of the logged in user.

    requires:
    - old_password
    - new_password

    Password must be atleast 8 characters long and contain atleast one letter and one number
    """
    if old_password is None:
        raise HTTPException(status_code=400, detail="Old password not provided")

    curr_user = await Users.get(username=user.username)
    old_hash = curr_user.password_hash
    if not verify_password(old_password, old_hash):
        raise HTTPException(status_code=401, detail="Incorrect old password")

    if new_password is None:
        raise HTTPException(status_code=400, detail="New password not provided")
    if re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", new_password) is None:
        raise HTTPException(
            status_code=400,
            detail="Password must be atleast 8 characters long and contain atleast one letter and one number",
        )
    new_password = get_hashed_password(new_password)
    await Users.filter(username=user.username).update(password_hash=new_password)
    return JSONResponse(
        content={"detail": "Password changed successfully"}, status_code=200
    )
