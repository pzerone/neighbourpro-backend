"""
Title: Global dependencies
File: /dependencies.py
Description: This file contains the global dependencies for the app.
Author: github.com/pzerone
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from jose import jwt
import os

SECRET_KEY = os.environ["JWT_SECRET"]
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET"]
ALGORITHM = os.environ["JWT_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ["JWT_AT_EXPIRE_MINUTES"]
REFRESH_TOKEN_EXPIRE_MINUTES = os.environ["JWT_RT_EXPIRE_MINUTES"]


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    email: str | None = None


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def create_access_token(subject: TokenData, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + timedelta(minutes=float(expires_delta))
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=float(ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {
        "exp": expires_delta,
        "username": subject.username,
        "email": subject.email,
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: TokenData, expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + timedelta(minutes=float(expires_delta))
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes=float(REFRESH_TOKEN_EXPIRE_MINUTES)
        )

    to_encode = {
        "exp": expires_delta,
        "username": subject.username,
        "email": subject.email,
    }
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_token
    except:
        return None
