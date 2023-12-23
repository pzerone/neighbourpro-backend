"""
Title: Models
File: /database/models.py
Description: This file contains the tortoise ORM models for the database.
Author: github.com/pzerone
"""

from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    #: Auto generated
    id = fields.IntField(pk=True)
    #: Should be a uuid and internal only. not for front end.
    username = fields.CharField(max_length=20, unique=True)
    first_name = fields.CharField(max_length=50, null=False)
    last_name = fields.CharField(max_length=50, null=True)

    email = fields.CharField(max_length=100, null=False)
    is_worker = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=20, null=False)
    password_hash = fields.CharField(max_length=128, null=False)

    House_name = fields.CharField(max_length=50, null=True)
    Street = fields.CharField(max_length=50, null=True)
    City = fields.CharField(max_length=50, null=True)
    State = fields.CharField(max_length=50, null=True)
    Pincode = fields.IntField(max_length=6, null=True)

    Latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)
    Longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def full_name(self) -> str:
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name

    class PydanticMeta:
        computed = ["full_name"]
        exclude = ["created_at", "modified_at", "House_name", "Street", "City", "State", "Pincode", "Latitude", "Longitude"]


User_Pydantic = pydantic_model_creator(Users, name="User")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)
