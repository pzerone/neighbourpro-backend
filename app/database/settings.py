import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ["DB_URL"]

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["aerich.models", "app.database.models"],
            "default_connection": "default",
        },
    },
    # Refer: https://tortoise.github.io/timezone.html
    "use_tz": False,  # If True, then the datetime fields will be timezone aware (UTC)
    "timezone": "UTC",  # Make Tortoise aware which timezone database is using
}
