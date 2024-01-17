"""
Title: NeighbourPro backend API
File: /main.py
Description: This file contains the main FastAPI app of NeighbourPro backend.
Author: github.com/pzerone
"""

import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.environ["DB_URL"]

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from tortoise import Tortoise

Tortoise.init_models(
    ["database.models"], "models"
)  # Initialize models as soon as the app starts so that table relations are properly set up

from routers import auth, work, users, admin

app = FastAPI(openapi_url="/apidocs")
origins = ["*"]

app.include_router(auth.router)
app.include_router(work.router)
app.include_router(users.router)
app.include_router(admin.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Check health route"""
    return {"message": "hello world"}


register_tortoise(
    app,
    config={
        "connections": {"default": DB_URL},
        "apps": {
            "models": {
                "models": ["database.models"],
                "default_connection": "default",
            },
        },
        "use_tz": False,
        "timezone": "Asia/Kolkata",
    },
    add_exception_handlers=True,
)
