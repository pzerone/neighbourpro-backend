import os
from geopy.distance import geodesic
import numpy as np
from app.database.models import Reviews

weights = {
    "distance": float(os.environ["DISTANCE_WEIGHT"]),
    "review_count": float(os.environ["REVIEW_COUNT_WEIGHT"]),
    "cost": float(os.environ["COST_WEIGHT"]),
    "rating": float(os.environ["RATING_WEIGHT"]),
}


def calculate_score(
    distance: float,
    rating: float,
    review_count: int,
    hourly_cost: float,
    mean_hourly_cost_other: float,
    weights: dict,
) -> float:
    """
    Calculate the score for a worker based on various factors.

    Args:
    - distance: Distance between the worker and the user (in meters)
    - rating: Average rating of the worker from previous bookings
    - review_count: Number of reviews that made up the average rating
    - hourly_cost: Hourly cost of the worker
    - mean_hourly_cost_other: Mean hourly cost of other workers in the same profession
    - weights: Dictionary containing weights for each factor

    Returns:
    - score: Calculated score for the worker
    """
    if distance > 0:
        distance_factor = weights["distance"] / np.square(distance)
    else:
        distance_factor = 0
    if review_count > 0:
        review_count_factor = weights['review_count'] / np.sqrt(review_count)
    else:
        review_count_factor = 0
    cost_factor = weights["cost"] * (mean_hourly_cost_other / hourly_cost)
    score = (
        weights["rating"] * rating + review_count_factor + cost_factor + distance_factor
    )
    return score


async def get_review_count(worker_id: int):
    return await Reviews.filter(worker_id=worker_id).count()


def calulate_distane_in_km(cords_1: tuple, cords_2: tuple) -> float:
    return geodesic(cords_1, cords_2).kilometers


async def sort_workers_by_score(
    workers: list, user_cords: tuple, mean_hourly_rate: float
):
    sorted_workers = []
    for worker in workers:
        worker_dict = worker.model_dump()
        worker_avg_rating = worker_dict.get("worker")[0].get("avg_rating")
        worker_review_count = await get_review_count(worker_dict.get("id"))
        worker_hourly_rate = worker_dict.get("worker")[0].get("hourly_rate")
        worker_cords = (
            float(
                worker_dict.get("user")[0].get("latitude")
            ),  # why did the serializer put the json inside a list when there is nothing else there
            float(worker_dict.get("user")[0].get("longitude")),
        )
        distance_to_user = calulate_distane_in_km(user_cords, worker_cords)
        score =  calculate_score(
            distance_to_user,
            worker_avg_rating,
            worker_review_count,
            worker_hourly_rate,
            mean_hourly_rate,
            weights
        )
        worker_dict["score"] = score
        if 'user' in worker_dict: del worker_dict['user']
        sorted_workers.append(worker_dict)
    return sorted_workers
