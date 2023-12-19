import os
import dotenv

dotenv.load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from routers import users


app = FastAPI()
origins = ["*"]

app.include_router(users.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_url = os.getenv("DB_URL")


@app.get("/")
async def root():
    return {"message": "hello from root"}


register_tortoise(
    app,
    db_url=db_url,
    modules={"models": ["database.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
