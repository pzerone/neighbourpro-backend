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
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise import timezone
from app.dependencies import TokenData
from app.database.models import Users, Professions
from app.routers.auth import get_current_user


class Address(BaseModel):
    House_name: str
    Street: str | None
    City: str
    State: str
    Pincode: int
    Latitude: float
    Longitude: float


class WorkerUpgrade(BaseModel):
    profession_id: int
    hourly_rate: float
    worker_bio: str


professions_data = pydantic_model_creator(
    Professions,
    name="profession_data_input",
    include=("id", "name", "description", "estimated_time_hours"),
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.put("/update-address")
async def add_address(
    user: TokenData = Depends(get_current_user), address: Address = None
):
    """
    This route is used to add an address to the user. Address is required for a user to be a professional,
    booking a work, etc.

    requires:
    - House_name
    - Street
    - City
    - State
    - Pincode
    - Latitude
    - Longitude
    """
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
        modified_at=timezone.now(),
    )
    return JSONResponse(
        content={"detail": "Address added successfully"}, status_code=200
    )


@router.get("/professions", response_model=List[professions_data])
async def get_professions():
    """
    This route is used to get all the professions available in the database.
    """
    return await professions_data.from_queryset(Professions.all())


@router.get("/professions/{profession_id}", response_model=professions_data)
async def get_profession(profession_id: int):
    """
    This route is used to get a profession for a given profession id.

    requires:
    - profession_id

    Note: This route does not return any extra data than the /professions route, keeping this since we might have more data about a profession to be send to user in future
    """
    try:
        profession = await professions_data.from_queryset_single(
            Professions.get(id=profession_id)
        )
    except:
        raise HTTPException(status_code=400, detail="Profession does not exist")
    return profession


@router.put("/switch-to-professional")
async def switch_to_professional(
    user: TokenData = Depends(get_current_user), details: WorkerUpgrade = None
):
    """
    This route is used to switch a user to a professional.

    requires:
    - profession_id
    - hourly_rate
    - worker_bio
    """
    # If the user is already a professional, then do not allow switching
    if user.role == "worker":
        raise HTTPException(status_code=400, detail="Already a professional")

    if details is None:
        raise HTTPException(status_code=400, detail="Details not provided")

    if details.hourly_rate <= 0:
        raise HTTPException(
            status_code=400, detail="Hourly rate must be greater than 0"
        )

    curr_user = await Users.filter(username=user.username).first()
    if curr_user.House_name is None:
        raise HTTPException(status_code=400, detail="User does not have valid address")

    profession_exists = await Professions.filter(id=details.profession_id)
    if not profession_exists:
        raise HTTPException(status_code=400, detail="Profession does not exist")

    await Users.filter(username=user.username).update(
        profession_id=details.profession_id,
        role="worker",
        hourly_rate=details.hourly_rate,
        worker_bio=details.worker_bio,
        modified_at=timezone.now(),
    )
    return JSONResponse(
        content={"detail": "switched to professional succesfully"}, status_code=200
    )


@router.get("/recommend")
async def get_recommendations(user: TokenData = Depends(get_current_user)):
    """
    This route is used to get recommended professions for a user. Uses collaborative filtering.
    """

    # TODO: Use collaborative filtering to get recommendations

    # Dummy data for now
    professions = await professions_data.from_queryset(Professions.all())
    return {
        "recommendations": professions,
        "Based on your recent activity": professions,
    }
