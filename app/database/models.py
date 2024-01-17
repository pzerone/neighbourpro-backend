"""
Title: Models
File: /database/models.py
Description: This file contains the tortoise ORM models for the database.
Author: github.com/pzerone
"""

from tortoise import fields, models
from tortoise.contrib.postgres.fields import ArrayField


# TODO: Add user_avg_rating field to Users model for workers


class Professions(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20, unique=True)
    description = fields.TextField(null=True)
    estimated_time_hours = fields.FloatField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    # created_by = fields.ForeignKeyField(                                #
    #     "models.Users", related_name="professions", null=False          #
    # )                                                                   # TODO: Fix cyclic foreign key reference
    # modified_by = fields.ForeignKeyField(                               # Add an extra table for these metadata to break the cyclic reference
    #     "models.Users", related_name="professions_modified", null=False #
    # )

    class PydanticMeta:
        exclude = ["id", "created_at", "modified_at"]


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    first_name = fields.CharField(max_length=50, null=False)
    last_name = fields.CharField(max_length=50, null=True)

    role = fields.CharField(max_length=10, null=False, default="user")
    profession: fields.ForeignKeyRelation[Professions] = fields.ForeignKeyField(
        "models.Professions", related_name="profession", null=True
    )
    hourly_rate = fields.FloatField(null=True)
    worker_bio = fields.TextField(null=True)

    email = fields.CharField(max_length=100, null=False)
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
        exclude = ["created_at", "modified_at"]


class Works(models.Model):
    id = fields.IntField(pk=True)
    tags = ArrayField(null=True, element_type="text")
    user_description = fields.TextField(null=True)
    scheduled_date = fields.DateField(null=True)
    scheduled_time = fields.TimeField(null=True)

    booked_by: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="booked_by", null=False
    )
    assigned_to: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="assigned_to", null=False
    )
    profession: fields.ForeignKeyRelation[Professions] = fields.ForeignKeyField(
        "models.Professions", related_name="profession_type", null=False
    )
    status = fields.CharField(max_length=20, null=False, default="pending")
    payment_status = fields.CharField(max_length=20, null=False, default="pending")

    estimated_cost = fields.FloatField(null=True)
    final_cost = fields.FloatField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class PydanticMeta:
        exclude = ["created_at", "modified_at", "booked_by"]


class Reviews(models.Model):
    id = fields.IntField(pk=True)
    rating = fields.IntField(null=False)  # 1 to 5
    review = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    user_id: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="user_id", null=False
    )
    worker_id: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="worker_id", null=False
    )

    class PydanticMeta:
        exclude = ["created_at", "modified_at", "reviewed_by", "reviewed_to"]
