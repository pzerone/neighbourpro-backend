"""
Title: Work router
File: /routers/work.py
Description: This file contains the FastAPI router for work views.
Author: github.com/pzerone
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel
from database.models import Users
from dependencies import TokenData
from .users import get_current_user

router = APIRouter(
    prefix="/work",
    tags=["work"],
)


@router.post("/create")
async def create_work(user: TokenData = Depends(get_current_user)):
    current_user = await Users.get(username=user.username)
    if not current_user.Latitude or not current_user.Longitude:
        raise HTTPException(status_code=400, detail="User address not found")

    return JSONResponse(
        content={
            "detail": "The server refuses the attempt to brew coffee with a teapot."
        },
        status_code=418,
    )
