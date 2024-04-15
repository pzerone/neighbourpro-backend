from geopy.distance import geodesic
from score import calculate_score

weights = {"distance": 0.4, "rating": 0.3, "review_count": 0.2, "cost": 0.1}


def calculate_distance(cords_first: tuple, cords_second: tuple) -> float:
    return geodesic(cords_first, cords_second).kilometers


if __name__ == "__main__":
    fcords = (
        (8.48781087926209, 76.95154963222026),
        (9.97190638587515, 76.32356863707346),
    )
    scords = (
        (8.4877956032228, 76.95155001051523),
        (8.6943855237142, 76.81930973794456),
    )
    dis1 = calculate_distance(fcords[0], fcords[1])
    dis2 = calculate_distance(scords[0], scords[1])
    print("Score 1", calculate_score(dis1, 4.5, 20, 500, 520, weights))
    print("Score 2", calculate_score(dis2, 4.5, 20, 500, 520, weights))
