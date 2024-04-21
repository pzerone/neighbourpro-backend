import pickle
from itertools import product
import pandas as pd

with open("model.bin", "rb") as file:
    model = pickle.load(file)


def get_top_n_recommendations(
    history: pd.DataFrame, user_id: int, count: int
) -> list[tuple]:
    past_selections = set(
        history[history["booked_by_id"] == user_id]["profession_id"]
    )
    all_professions = set(history["profession_id"])
    unconsidered_professions = all_professions - past_selections

    predictions = [
        (profession_id, model.predict(user_id, profession_id).est)
        for profession_id in unconsidered_professions
    ]
    top_n = sorted(predictions, key=lambda x: x[1], reverse=False)[:count]

    return top_n


def have_booked(user, profession, history: list):
    return (
        1
        if any(
            record["booked_by_id"] == user and record["profession_id"] == profession
            for record in history
        )
        else 0
    )


def dict_to_pd_df(
    history: list, unique_profession_ids: list, unique_user_ids: list
) -> pd.DataFrame:
    cols = ["booked_by_id", "profession_id", "booked_or_not"]
    df = pd.DataFrame(
        [
            [user_id, profession_id, have_booked(user_id, profession_id, history)]
            for user_id, profession_id in product(
                unique_user_ids, unique_profession_ids
            )
        ],
        columns=cols,
    )
    return df
