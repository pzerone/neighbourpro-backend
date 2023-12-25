"""
Title: Admin router
File: /routers/admin.py
Description: This file contains the FastAPI router for admin views.
Author: github.com/pzerone
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from database.models import (
    Professions,
    ProfessionsIn_Pydantic,
)
from dependencies import TokenData
from .auth import get_current_user


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


@router.post("/add-profession")
async def add_profession(
    user: TokenData = Depends(get_current_user),
    profession: ProfessionsIn_Pydantic = None,
):
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession is None:
        raise HTTPException(status_code=400, detail="Profession not provided")

    profession_exists = await Professions.filter(name=profession.name)
    if profession_exists:
        raise HTTPException(status_code=400, detail="Profession already exists")

    await Professions.create(
        **profession.model_dump(), created_by_id=user.id, modified_by_id=user.id
    )
    return JSONResponse(
        content={"detail": "Profession added successfully"}, status_code=201
    )


@router.put("/update-profession")
async def update_profession(
    user: TokenData = Depends(get_current_user),
    profession: ProfessionsIn_Pydantic = None,
    profession_id: int = None,
):
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession_id is None:
        raise HTTPException(status_code=400, detail="Profession not provided")

    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=400, detail="Profession does not exist")

    await Professions.filter(id=profession_id).update(
        **profession.model_dump(), modified_by_id=user.id
    )
    return JSONResponse(
        content={"detail": "Profession updated successfully"}, status_code=201
    )


@router.delete("/delete-profession")
async def delete_profession(
    user: TokenData = Depends(get_current_user), profession_id: int = None
):
    if user.role != "admin":
        raise HTTPException(status_code=401, detail="Unauthorized")

    if profession_id is None:
        raise HTTPException(status_code=400, detail="Profession not provided")

    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    await Professions.filter(id=profession_id).delete()
    return JSONResponse(
        content={"detail": "Profession deleted successfully"}, status_code=200
    )
