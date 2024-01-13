import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ["DB_URL"]

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["aerich.models", "models"],
            "default_connection": "default",
        },
    },
}