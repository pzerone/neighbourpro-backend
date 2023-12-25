"""
Title: Users router
File: /routers/users.py
Description: This file contains the FastAPI router for user views.
Author: github.com/pzerone
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dependencies import TokenData
from database.models import Users, Professions, Professions_Pydantic
from routers.auth import get_current_user


class Address(BaseModel):
    House_name: str
    Street: str | None
    City: str
    State: str
    Pincode: int
    Latitude: float
    Longitude: float


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.put("/update-address")
async def add_address(
    user: TokenData = Depends(get_current_user), address: Address = None
):
    if address is None:
        raise HTTPException(status_code=400, detail="Address not provided")

    await Users.filter(username=user.username).update(
        House_name=address.House_name,
        Street=address.Street,
        City=address.City,
        State=address.State,
        Pincode=address.Pincode,
        Latitude=address.Latitude,
        Longitude=address.Longitude,
    )
    return JSONResponse(
        content={"detail": "Address added successfully"}, status_code=200
    )


@router.get("/get-professions", response_model=List[Professions_Pydantic])
async def get_professions():
    return await Professions_Pydantic.from_queryset(Professions.all())


@router.put("/switch-to-professional")
async def switch_to_professional(
    user: TokenData = Depends(get_current_user), profession_id: int = None
):
    # If the user is already a professional, then do not allow switching
    if user.role == "worker":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession_id is None:
        raise HTTPException(status_code=400, detail="Profession not provided")

    curr_user = await Users.filter(username=user.username).first()
    if curr_user.House_name is None:
        raise HTTPException(status_code=400, detail="User does not have valid address")

    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=400, detail="Profession does not exist")

    await Users.filter(username=user.username).update(
        profession_id=profession_id, role="worker"
    )
    return JSONResponse(
        content={"detail": "switched to professional succesfully"}, status_code=200
    )
