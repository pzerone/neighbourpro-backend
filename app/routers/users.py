"""
Title: Users router
File: /routers/users.py
Description: This file contains the FastAPI router for user views.
Author: github.com/pzerone
"""

from typing import TypeAlias
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from tortoise import timezone
from tortoise.transactions import in_transaction
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.exceptions import DoesNotExist, OperationalError
from app.dependencies import TokenData
from app.database.models import Users, UserDetails, WorkerDetails, Professions, Works
from app.routers.auth import get_current_user
from app.utils.logger import msg_logger
from app.utils.recommend import dict_to_pd_df, get_top_n_recommendations


class Address(BaseModel):
    house_name: str
    street: str | None
    city: str
    state: str
    pincode: int
    phone_number: str
    latitude: float
    longitude: float


class WorkerUpgrade(BaseModel):
    profession_id: int
    hourly_rate: float
    worker_bio: str


professions_data: TypeAlias = pydantic_model_creator(
    Professions,
    name="profession_data_output",
    include=(
        "id",
        "name",
        "description",
        "estimated_time_hours",

        )
    # exclude_readonly=True,
)  # type: ignore

works_history: TypeAlias = pydantic_model_creator(
    Works,
    name="work_history_output",
    include=("profession_id", "booked_by_id"),
)  # type ignore


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/address")
async def add_address(
    user: TokenData = Depends(get_current_user), address: Address = None
):
    """
    This route is used to add an address to the user. Address is required for a user to be a professional,
    booking a work, etc.

    requires:
    - Phone number
    - House name
    - Street
    - City
    - State
    - Pincode
    - Latitude
    - Longitude
    """
    if address is None:
        raise HTTPException(status_code=400, detail="Address not provided")
    
    address_check = await UserDetails.filter(user_id=user.id)
    if len(address_check) > 0:
        raise HTTPException(status_code=400, detail="Address already exists. Update if needed.")

    await UserDetails.create(
        user_id=user.id,
        **address.model_dump(exclude_unset=True),
        created_at=timezone.now(),
        modified_at=timezone.now(),
    )
    return JSONResponse(
        content={"detail": "Address added successfully"}, status_code=200
    )


@router.put("/address")
async def update_address(address: Address, user: TokenData = Depends(get_current_user)):
    """
    This route is used to update the address of a user.

    requires:
    - Phone number
    - House name
    - Street
    - City
    - State
    - Pincode
    - Latitude
    - Longitude
    """
    try:
        await UserDetails.get(user_id=user.id)
    except DoesNotExist:
        raise HTTPException(
            status_code=400,
            detail="User does not have valid address. Please add an address first.",
        )
    await UserDetails.filter(user_id=user.id).update(
        **address.model_dump(exclude_unset=True), modified_at=timezone.now()
    )

    return JSONResponse(
        content={"detail": "Address updated successfully"}, status_code=200
    )


@router.get("/professions", response_model=list[professions_data])
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
    except DoesNotExist:
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

    try:
        await UserDetails.get(user_id=user.id)
    except DoesNotExist:
        raise HTTPException(
            status_code=400,
            detail="User does not have valid address. Please add an address first.",
        )

    profession_exists = await Professions.filter(id=details.profession_id)
    if not profession_exists:
        raise HTTPException(status_code=400, detail="Profession does not exist")

    try:
        async with in_transaction() as conn:
            await Users.filter(id=user.id).using_db(conn).update(role="worker")
            await WorkerDetails.create(
                using_db=conn,
                user_id=user.id,
                profession_id=details.profession_id,
                hourly_rate=details.hourly_rate,
                worker_bio=details.worker_bio,
                created_at=timezone.now(),
                modified_at=timezone.now(),
            )
    except OperationalError as e:
        msg_logger(
            f"Switch to professional failed: {user.username} failed to switch to professional due to database error.\n{e}",
            40,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to switch to professional. Please try again later.",
        )
    return JSONResponse(
        content={"detail": "switched to professional succesfully"}, status_code=200
    )


@router.get("/recommend")
async def get_recommendations():
    """
    This route is used to get recommended professions for a user. Uses collaborative filtering.
    """

    # TODO: Use collaborative filtering to get recommendations

    # Dummy data for now
    professions = await professions_data.from_queryset(Professions.all())
    return {
        "recommendations": professions,
        "based on your recent activity": professions,
    }


@router.get("/recommend/v2")
async def get_real_recommendations(user: TokenData = Depends(get_current_user)):

    booked_works = await Works.filter(booked_by_id=user.id, status="closed")
    if len(booked_works) < 1:
        msg_logger(f"Recommend: user{user.id} does not have any booking history. count: {len(booked_works)}. skipping prediction", 20)
        # If the user does not have any past booking history, model will not generate recommendations
        # hence send all professions and let frontend show random professions
        professions = await professions_data.from_queryset(Professions.all())
        return {
            "real": False,
            "recomendations": professions,
        }
    past_works_pydantic = await works_history.from_queryset(Works.all())
    work_history_list_of_dict = [item.dict() for item in past_works_pydantic]

    user_id_list = await Users.all().values_list("id", flat=True)
    profession_id_list = await Professions.all().values_list("id", flat=True)
    history_df = dict_to_pd_df(
        work_history_list_of_dict, profession_id_list, user_id_list
    )

    top_n_recommendations = get_top_n_recommendations(history_df, user.id, 5)
    if (
        len(top_n_recommendations) > 0
    ):  # Only if recommendations are generated by the model
        professions = await professions_data.from_queryset(
            Professions.filter(id__in=top_n_recommendations)
        )
        return {
            "real": True,
            "recommendations": professions,
        }
    professions = await professions_data.from_queryset(Professions.all())
    msg_logger(f"Recommend: Algo prediction returned empty list. count: {len(top_n_recommendations)}. sending all", 20)
    return {
        "real": False,
        "recomendations": professions,
    }
