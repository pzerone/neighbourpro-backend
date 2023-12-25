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

from routers import auth, work, users, admin

app = FastAPI()
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
    return {"message": "hello from root"}


register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["database.models"]},
    add_exception_handlers=True,
    # generate_schemas=True,
)
