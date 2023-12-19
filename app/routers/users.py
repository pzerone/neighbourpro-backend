from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from database.models import Users, UserIn_Pydantic
from tortoise.expressions import Q
import re
from dependencies import (
    get_hashed_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    Token,
    TokenData,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    # dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
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


@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        user = await Users.get(username=form_data.username)
    except:
        return JSONResponse(
            content={"detail": "Invalid username of password"}, status_code=404
        )

    if not verify_password(form_data.password, user.password_hash):
        return JSONResponse(
            content={"detail": "Invalid username of password"}, status_code=404
        )

    token_data = TokenData(username=user.username, email=user.email)
    return Token(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        token_type="bearer",
    )
