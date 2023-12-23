import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ["DB_URL"]

TORTOISE_ORM = {
    "connections": {"default": db_url},
    "apps": {
        "models": {
            "models": ["aerich.models", "models"],
            "default_connection": "default",
        },
    },
}