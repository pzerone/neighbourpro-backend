"""
Title: Work router
File: /routers/work.py
Description: This file contains the FastAPI router for work views.
Author: github.com/pzerone
"""

from typing import TypeAlias
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.exceptions import DoesNotExist, OperationalError
from tortoise.functions import Avg
from tortoise import timezone
from tortoise.transactions import in_transaction
from app.database.models import (
    UserDetails,
    Users,
    Professions,
    WorkerDetails,
    Works,
    Reviews,
)
from app.dependencies import TokenData
from app.routers.auth import get_current_user
from app.utils.score import sort_workers_by_score
from app.utils.logger import msg_logger

professionals_data: TypeAlias = pydantic_model_creator(
    Users,
    name="Professionals Data Output",
    include=(
        "id",
        "first_name",
        "last_name",
        "worker",
        "user",
    ),
)  # type: ignore

work_create_in: TypeAlias = pydantic_model_creator(
    Works,
    name="Create Work Data Input",
    exclude_readonly=True,
    include=(
        "tags",
        "user_description",
        "profession_id",
        "scheduled_date",
        "scheduled_time",
        "assigned_to_id",
    ),
)  # type: ignore

work_details_out: TypeAlias = pydantic_model_creator(
    Works,
    name="Work Details Data Output",
    include=(
        "id",
        "tags",
        "user_description",
        "assigned_to_id",
        "booked_by_id",
        "profession_id",
        "status",
        "payment_status",
        "estimated_cost",
        "scheduled_date",
        "scheduled_time",
        "final_cost",
        "created_at",
        "modified_at",
    ),
)  # type: ignore

client_details: TypeAlias = pydantic_model_creator(
    UserDetails,
    name="Client Details Data Output",
    include=(
        "latitude",
        "longitude",
        "phone_number",
    ),
)  # type: ignore

review_in: TypeAlias = pydantic_model_creator(
    Reviews, name="Review Data Input", include=("rating", "review")
)  # type: ignore

router = APIRouter(
    prefix="/work",
    tags=["Work"],
)


@router.get("/professionals/{profession_id}/filter")
async def filter_professionals(
    profession_id: int, user: TokenData = Depends(get_current_user)
):
    try:
        await Professions.get(id=profession_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    professionals = await professionals_data.from_queryset(
        Users.filter(worker__profession__id=profession_id)
    )

    mean_hourly_rate = (
        await WorkerDetails.filter(profession_id=profession_id)
        .annotate(avg_hourly_rate=Avg("hourly_rate"))
        .values_list("avg_hourly_rate", flat=True)
    )[0]

    try:
        curr_user = await UserDetails.get(user_id=user.id)
    except DoesNotExist:
        raise HTTPException(
            status_code=500,
            detail="User not in database. You should't have hit this, yet here you are.",
        )
    user_cords = (curr_user.latitude, curr_user.longitude)
    return await sort_workers_by_score(
        workers=professionals,
        user_cords=user_cords,
        mean_hourly_rate=mean_hourly_rate,
    )


@router.get("/professionals/{profession_id}", response_model=list[professionals_data])
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
        Users.filter(worker__profession__id=profession_id)
    )


@router.get("/estimated-cost/{worker_id}")
async def get_estimated_cost(worker_id: int):
    """
    This route is used to get the estimated cost for a given worker.

    requires:
    - Worker's user_id

    returns:
    - estimated_cost
    """
    try:
        worker = await WorkerDetails.get(user__id=worker_id)
    except:
        raise HTTPException(status_code=404, detail="Professional does not exist")

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
    This route is used to book a work. scheduled_time must be timezone naive and in UTC time.

    requires:
    - List of tags(Optional)
    - user_description
    - assigned_to
    - profession_id
    - scheduled_date
    - scheduled_time
    """
    current_user = await Users.get(id=user.id)
    try:
        await UserDetails.get(user__id=current_user.id)
    except DoesNotExist:
        raise HTTPException(
            status_code=400, detail="User does not have valid address to create a work"
        )

    try:
        await Professions.get(id=work.profession_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Profession does not exist")

    if user.id == work.assigned_to_id:
        raise HTTPException(status_code=400, detail="User cannot self assign work")

    try:
        booked_worker = await WorkerDetails.get(user__id=work.assigned_to_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Professional does not exist")

    await booked_worker.fetch_related("profession")
    if booked_worker.profession.id != work.profession_id:
        raise HTTPException(
            status_code=400,
            detail="selected worker is not a professional of selected profession",
        )

    if work.scheduled_date < timezone.now().date():
        raise HTTPException(
            status_code=400,
            detail="Scheduled date is in the past. Only future works can be booked",
        )
    if timezone.is_aware(work.scheduled_time):
        raise HTTPException(
            status_code=400,
            detail="""Scheduled time should not be timezone aware. Only naive time is allowed. Conversion to aware time is done automatically. Eg: 10:00:00 instead of 10:00:00+05:30""",
        )
    if work.scheduled_date < timezone.now().date() or (
        work.scheduled_date == timezone.now().date()
        and work.scheduled_time < timezone.now().time()
    ):
        raise HTTPException(
            status_code=400,
            detail="Scheduled time is in the past. Only future works can be booked",
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


@router.get("/booked-works", response_model=list[work_details_out])
async def get_my_works(user: TokenData = Depends(get_current_user)):
    """
    This route is used to get the list of works created by the user.

    returns:
    - List of works
    """
    return await work_details_out.from_queryset(Works.filter(booked_by_id=user.id))


@router.get("/assigned-works", response_model=list[work_details_out])
async def get_assigned_works(user: TokenData = Depends(get_current_user)):
    """
    This route is used to get the list of works assigned to the worker.
    User must be a worker to access this route.

    returns:
    - List of works
    """
    if user.role != "worker":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await work_details_out.from_queryset(Works.filter(assigned_to_id=user.id))


@router.post("/accept-work/{work_id}")
async def accept_work(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to accept a work.
    User must be the assigned worker of the work to access this route.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Work is not in pending state. Only pending works can be accepted",
        )
    if work.scheduled_date < timezone.now().date():
        await Works.filter(id=work_id).update(
            status="expired", modified_at=timezone.now()
        )
        raise HTTPException(
            status_code=400,
            detail="Work already expired. Only future works can be accepted",
        )
    # work.scheduled_time is timezone aware(Do not know which part of the stack adds the timezone).
    # Hence we need to convert timezone.now().time() to aware time for comparison since
    # timezone.now().time() is timezone naive
    if work.scheduled_time < timezone.make_aware(timezone.now().time()):
        await Works.filter(id=work_id).update(
            status="expired", modified_at=timezone.now()
        )
        raise HTTPException(
            status_code=400,
            detail="Work already expired. Only future works can be accepted",
        )

    await Works.filter(id=work_id).update(status="accepted", modified_at=timezone.now())
    return JSONResponse(
        content={"detail": "Work accepted sucessfully"}, status_code=200
    )


@router.post("/cancel-work/{work_id}")
async def cancel_work(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to cancel a work.
    User must be the creator of the work to cancel it.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.booked_by_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Work is not in pending state. Only pending works can be cancelled",
        )

    await Works.filter(id=work_id).update(
        status="cancelled", modified_at=timezone.now()
    )
    return JSONResponse(
        content={"detail": "Work cancelled sucessfully"}, status_code=200
    )


@router.post("/reject-work/{work_id}")
async def reject_work(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to reject a work.
    User must be the assigned worker of the work to access this route.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Work is not in pending state. Only pending works can be rejected",
        )

    if work.scheduled_date < timezone.now().date():
        await Works.filter(id=work_id).update(
            status="expired", modified_at=timezone.now()
        )
        raise HTTPException(
            status_code=400,
            detail="Work already expired. Only future works can be rejected",
        )
    if work.scheduled_time < timezone.make_aware(timezone.now().time()):
        await Works.filter(id=work_id).update(
            status="expired", modified_at=timezone.now()
        )
        raise HTTPException(
            status_code=400,
            detail="Work already expired. Only future works can be rejected",
        )

    await Works.filter(id=work_id).update(status="rejected", modified_at=timezone.now())
    return JSONResponse(
        content={"detail": "Work rejected sucessfully"}, status_code=200
    )


@router.get("/client-contact-details/{work_id}")
async def get_client_contact_details(
    work_id: int, user: TokenData = Depends(get_current_user)
):
    """
    This route is used to get the contact information of the client.
    This information includes the full name, address, cordinates and phone number of the client for a given work id.
    User must be the assigned worker of the work to access this route.

    requires:
    - work_id

    returns:
    - Full Name
    - First Name
    - Last Name
    - House Name
    - Street
    - City
    - State
    - Pincode
    - Latitude
    - Longitude
    - Phone Number
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Work is not in accepted state. Accept the work before getting client details",
        )

    tester = await UserDetails.get(user_id=work.booked_by_id)
    return await client_details.from_tortoise_orm(tester)


@router.post("/start-work/{work_id}")
async def start_work(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to start a work.
    User must be the assigned worker of the work to access this route.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="Work is not in accepted state. Accept the work before starting it",
        )

    await Works.filter(id=work_id).update(status="started", modified_at=timezone.now())
    return JSONResponse(content={"detail": "Work started sucessfully"}, status_code=200)


@router.post("/quote-final-cost/{work_id}")
async def quote_final_cost(
    work_id: int, final_cost: float, user: TokenData = Depends(get_current_user)
):
    """
    This route is used to quote the final cost of a work.
    User must be the assigned worker of the work to access this route.

    requires:
    - work_id
    - final_cost
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "started":
        raise HTTPException(
            status_code=400,
            detail="Work is not yet in started state. Only started works can be quoted",
        )

    await Works.filter(id=work_id).update(
        final_cost=final_cost, modified_at=timezone.now()
    )
    return JSONResponse(
        content={"detail": "Final cost quoted sucessfully"}, status_code=200
    )


@router.post("/recieved-payment/{work_id}")
async def recieve_payment(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to mark a work as payment received.
    User must be the assigned worker of the work to access this route.
    Payment system works in mutual agreement between a client and worker.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.assigned_to_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "started":
        raise HTTPException(
            status_code=400,
            detail="Work is not yet in started state. Only started works can be paid for",
        )

    if work.final_cost == None:
        raise HTTPException(
            status_code=400,
            detail="Final cost is not quoted for the work. Quote the final cost before marking work as paid",
        )

    if (
        work.payment_status == "sent"
    ):  # If payment is already in "sent" state, the client has marked it as paid.
        await Works.filter(
            id=work_id
        ).update(  # Hence the worker cam mark it as received and close the work.
            payment_status="received", status="closed", modified_at=timezone.now()
        )

    else:  # If not, the worker can only update payment status.
        await Works.filter(id=work_id).update(
            payment_status="received", modified_at=timezone.now()
        )

    return JSONResponse(
        content={"detail": "Payment recieved sucessfully"}, status_code=200
    )


@router.post("/sent-payment/{work_id}")
async def send_payment(work_id: int, user: TokenData = Depends(get_current_user)):
    """
    This route is used to mark a work as payment sent.
    User must be the creator of the work to access this route.

    requires:
    - work_id
    """
    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.booked_by_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "started":
        raise HTTPException(
            status_code=400,
            detail="Work is not yet in started state. Only started works can be paid for",
        )

    if work.final_cost == None:
        raise HTTPException(
            status_code=400,
            detail="Final cost is not quoted for the work. Final cost must be quoted by the worker before marking work as paid",
        )

    if work.payment_status == "received":
        await Works.filter(
            id=work_id
        ).update(  # If payment is already in "received" state, the worker has marked it as paid.
            status="closed", modified_at=timezone.now()
        )

    else:  # If not, the client can only update payment status.
        await Works.filter(id=work_id).update(
            payment_status="sent", modified_at=timezone.now()
        )

    return JSONResponse(content={"detail": "Payment sent sucessfully"}, status_code=200)


@router.post("/review-work/{work_id}")
async def review_work(
    work_id: int, review: review_in, user: TokenData = Depends(get_current_user)
):
    """
    This route is used to review a work.
    User must be the creator of the work to access this route.

    requires:
    - work_id
    - review
    """
    if len(review.review) > 500:
        raise HTTPException(
            status_code=400,
            detail="Review cannot be more than 500 characters long",
        )

    if not 1 <= review.rating <= 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5",
        )

    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.booked_by_id != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if work.status != "closed":
        raise HTTPException(
            status_code=400,
            detail="Work is not yet in closed state. Only closed works can be reviewed",
        )

    if await Reviews.filter(work_id=work_id).exists():
        raise HTTPException(
            status_code=400,
            detail="Work is already reviewed. Only works that are not reviewed can be reviewed",
        )

    existing_reviews = await Reviews.filter(worker_id=work.assigned_to_id)
    reviews_count = len(existing_reviews) + 1
    reviews_sum = sum([review.rating for review in existing_reviews]) + review.rating
    new_avg_rating = reviews_sum / reviews_count

    try:
        async with in_transaction() as conn:
            await Reviews.create(
                using_db=conn,
                **review.dict(exclude_unset=True),
                user_id=user.id,
                work_id=work_id,
                worker_id=work.assigned_to_id,
                created_at=timezone.now(),
                modified_at=timezone.now(),
            )
            await WorkerDetails.filter(user_id=work.assigned_to_id).using_db(
                conn
            ).update(avg_rating=new_avg_rating)
    except OperationalError as e:
        msg_logger(
            f"Failed to review work. Tried new average rating: {new_avg_rating}", 40
        )
        raise HTTPException(status_code=500, detail="Failed to review work")

    msg_logger(f"Work reviewed sucessfully. New Average Rating: {new_avg_rating}", 20)

    return JSONResponse(
        content={"detail": "Work reviewed sucessfully"}, status_code=200
    )


@router.put("/review-work/{work_id}")
async def update_review(
    work_id: int, review: review_in, user: TokenData = Depends(get_current_user)
):
    """
    This route is used to update a review.
    User must be the creator of the work to access this route.

    requires:
    - work_id
    - review
    """
    if len(review.review) > 500:
        raise HTTPException(
            status_code=400,
            detail="Review cannot be more than 500 characters long",
        )

    if not 1 <= review.rating <= 5:
        raise HTTPException(
            status_code=400,
            detail="Rating must be between 1 and 5",
        )

    try:
        work = await Works.get(id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work id does not correspond to a valid work booking",
        )

    if work.booked_by != user.id:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        review_obj = await Reviews.get(work_id=work_id)
    except:
        raise HTTPException(
            status_code=404,
            detail="Work is not reviewed yet. Review the work first",
        )

    await Reviews.filter(id=review_obj.id).update(
        **review.dict(exclude_unset=True),
        edited=True,
        modified_at=timezone.now(),
    )
    return JSONResponse(
        content={"detail": "Work review updated sucessfully"}, status_code=200
    )
