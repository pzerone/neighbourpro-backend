"""
Title: Admin router
File: /routers/admin.py
Description: This file contains the FastAPI router for admin views.
Author: github.com/pzerone
"""

from typing import Optional, TypeAlias
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from app.database.models import Professions, Works
from app.dependencies import TokenData
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise import timezone
from app.routers.auth import get_current_user

profession_data: TypeAlias = pydantic_model_creator(
    Professions,
    name="profession_data_input",
    include=(
        "name",
        "description",
        "estimated_time_hours",
    ),
)  # type: ignore

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.post("/profession")
async def add_profession(
    user: TokenData = Depends(get_current_user),
    profession: profession_data = None,
):
    """
    This route is used to add a new profession - only for admin.

    requires:
    - name
    - description
    - estimated_time_hours
    """
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession is None:
        raise HTTPException(status_code=400, detail="Profession details not provided")

    profession_exists = await Professions.filter(name=profession.name)
    if profession_exists:
        raise HTTPException(status_code=400, detail="Profession already exists")

    await Professions.create(
        **profession.model_dump(),
        created_at=timezone.now(),
        modified_at=timezone.now(),
        created_by_id=user.id,
        modified_by_id=user.id,
    )
    return JSONResponse(
        content={"detail": "Profession added successfully"}, status_code=201
    )


@router.put("/profession/{profession_id}")
async def update_profession(
    user: TokenData = Depends(get_current_user),
    profession: profession_data = None,
    profession_id: Optional[int] = None,
):
    """
    This route is used to update a profession - only for admin.

    requires:
    - profession_id
    - name
    - description
    - estimated_time_hours
    """
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession_id is None:
        raise HTTPException(status_code=400, detail="Profession details not provided")

    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=400, detail="Profession does not exist")

    await Professions.filter(id=profession_id).update(
        **profession.model_dump(), modified_at=timezone.now(), modified_by_id=user.id
    )
    return JSONResponse(
        content={"detail": "Profession updated successfully"}, status_code=201
    )


@router.delete("/profession/{profession_id}")
async def delete_profession(
    user: TokenData = Depends(get_current_user), profession_id: Optional[int] = None
):
    """
    This route is used to delete a profession - only for admin.

    requires:
    - profession_id
    """
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession_id is None:
        raise HTTPException(status_code=400, detail="Profession id not provided")

    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    await Professions.filter(id=profession_id).delete()
    return JSONResponse(
        content={"detail": "Profession deleted successfully"}, status_code=200
    )


@router.get("/work/history")
async def list_work_history(user: TokenData = Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=400, detail="Unauthorized")

    return await works_history.from_queryset(Works.all().only("profession_id", "booked_by_id"))
