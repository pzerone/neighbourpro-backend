"""
Title: Work router
File: /routers/work.py
Description: This file contains the FastAPI router for work views.
Author: github.com/pzerone
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise import timezone
from database.models import Users, Professions, Works


from dependencies import TokenData
from routers.auth import get_current_user

professionals_data = pydantic_model_creator(
    Users,
    name="Professionals Data Output",
    include=(
        "id",
        "username",
        "first_name",
        "last_name",
        "hourly_rate",
        "worker_bio",
        "phone_number",
        "email",
    ),
)

work_create_in = pydantic_model_creator(
    Works,
    name="Create Work Data Input",
    exclude_readonly=True,
    exclude=(
        "status",
        "payment_status",
        "estimated_cost",
        "booked_by_id",
        "final_cost",
    ),
)

router = APIRouter(
    prefix="/work",
    tags=["Work"],
)


@router.get("/professionals/{profession_id}", response_model=List[professionals_data])
async def get_professionals(profession_id: int):
    """
    This route is used to get a list of professionals for a given profession id.
    This route contains the filtering algorithm for sorting workers (Yet to be implemented)

    requires:
    - profession_id
    """
    profession_exists = await Professions.filter(id=profession_id)
    if not profession_exists:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    # TODO: Use filtering algorithm for finding professionals.
    # TODO: Add pagination.
    return await professionals_data.from_queryset(
        Users.filter(profession=profession_id)
    )


@router.get("/estimated-cost/{worker_id}")
async def get_estimated_cost(worker_id: int):
    """
    This route is used to get the estimated cost for a given worker id.

    requires:
    - worker_id

    returns:
    - estimated_cost
    """
    try:
        worker = await Users.get(id=worker_id)
    except:
        raise HTTPException(status_code=404, detail="Professional does not exist")

    if worker.role != "worker":
        raise HTTPException(
            status_code=400, detail="Provided worker id does not correspond to a worker"
        )

    # fetch_related() is used to fetch the profession of the worker as it is a foreign key
    # and then we can use the profession to get the estimated time for the profession from db
    await worker.fetch_related("profession")

    # Estimated cost = hourly rate * estimated time
    estimated_cost = worker.hourly_rate * worker.profession.estimated_time_hours
    return estimated_cost


@router.post("/book-a-work")
async def create_work(
    work: work_create_in, user: TokenData = Depends(get_current_user)
):
    """
    This route is used to book a work.

    requires:
    - List of tags(Optional)
    - user_description
    - assigned_to
    - profession_id
    """
    current_user = await Users.get(id=user.id)
    if not current_user.Latitude or not current_user.Longitude:
        raise HTTPException(
            status_code=400, detail="User does not have valid address to create a work"
        )

    try:
        await Professions.get(id=work.profession_id)
    except:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    if user.id == work.assigned_to_id:
        raise HTTPException(status_code=400, detail="User cannot self assign work")

    try:
        booked_worker = await Users.get(id=work.assigned_to_id)
    except:
        raise HTTPException(status_code=404, detail="Professional does not exist")
    
    if booked_worker.role != "worker":
        raise HTTPException(
            status_code=400, detail="selected user is not a professional"
        )

    await booked_worker.fetch_related("profession")
    if booked_worker.profession.id != work.profession_id:
        raise HTTPException(
            status_code=400,
            detail="selected worker is not a professional of selected profession",
        )
    estimated_cost = (
        booked_worker.hourly_rate * booked_worker.profession.estimated_time_hours
    )
    await Works.create(
        **work.dict(exclude_unset=True),
        booked_by_id=user.id,
        status="pending",
        payment_status="pending",
        estimated_cost=estimated_cost,
        created_at=timezone.now(),
        modified_at=timezone.now(),
    )
    return JSONResponse(content={"detail": "Work creation sucessful"}, status_code=201)
