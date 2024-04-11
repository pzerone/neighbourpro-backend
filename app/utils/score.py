import numpy as np


def calculate_distance(cord1: tuple, cord2: tuple) -> float:
    return 1.2


def calculate_score(distance: float, rating: float, num_reviews: int, service_cost:float, cost_range, weights):
    """
    Calculate the score for a job worker based on distance, rating, and service cost.

    Parameters:
    - distance (float): Distance from the user.
    - rating (float): Rating of the worker.
    - num_reviews (int): Number of reviews for the worker.
    - service_cost (float): Service cost of the worker.
    - cost_range (tuple): Range of costs for workers of the same profession (min_cost, max_cost).
    - weights (dict): Dictionary containing weights for distance, rating, and service cost (w_D, w_R, w_C).

    Returns:
    - score (float): Calculated score for the job worker.
    """
    # Unpack weights
    w_D = weights.get("w_D", 1.0)
    w_R = weights.get("w_R", 1.0)
    w_C = weights.get("w_C", 1.0)

    # Non-linear decay function for distance
    distance_score = w_D * np.log(distance + 1)  # Example: Logarithmic decay

    # Handling edge cases for rating and number of reviews
    k = 1  # Smoothing factor
    rating_score = w_R * (rating * num_reviews / (num_reviews + k))

    # Service cost comparison within the range
    min_cost, max_cost = cost_range
    cost_diff = np.abs(service_cost - ((min_cost + max_cost) / 2))
    cost_range_score = w_C * (1 - cost_diff / (max_cost - min_cost))

    # Calculate total score
    score = distance_score + rating_score + cost_range_score

    return score


# Example usage:
distance = 5.0
rating = 4.5
num_reviews = 20
service_cost = 30.0
cost_range = (25.0, 35.0)
weights = {"w_D": 0.5, "w_R": 0.3, "w_C": 0.2}
