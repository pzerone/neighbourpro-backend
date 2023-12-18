from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from database.models import Users, UserIn_Pydantic
from tortoise.expressions import Q
from dependencies import get_hashed_password, verify_password
import re

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
    return JSONResponse(content={"message": "User creation sucessful"}, status_code=201)

