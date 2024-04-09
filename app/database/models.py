"""
Title: Models
File: /database/models.py
Description: This file contains the tortoise ORM models for the database.
Author: github.com/pzerone
"""

from tortoise import fields, models
from tortoise.contrib.postgres.fields import ArrayField


class Users(models.Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=20, unique=True)
    first_name = fields.CharField(max_length=50, null=False)
    last_name = fields.CharField(max_length=50, null=True)
    email = fields.CharField(max_length=100, null=False)
    password = fields.CharField(max_length=128, null=False)
    role = fields.CharField(max_length=10, null=False, default="user")
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()

    class PydanticMeta:
        exclude = ["role", "created_at", "modified_at"]


class UserDetails(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="user", null=False
    )
    phone_number = fields.CharField(max_length=20, null=False)
    house_name = fields.CharField(max_length=50, null=False)
    street = fields.CharField(max_length=50, null=False)
    city = fields.CharField(max_length=50, null=False)
    state = fields.CharField(max_length=50, null=False)
    pincode = fields.IntField(max_length=6, null=False)
    latitude = fields.DecimalField(max_digits=9, decimal_places=6, null=False)
    longitude = fields.DecimalField(max_digits=9, decimal_places=6, null=False)
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()

    class PydanticMeta:
        exclude = ["created_at", "modified_at"]


class WorkerDetails(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="worker", null=False
    )
    profession: fields.ForeignKeyRelation["Professions"] = fields.ForeignKeyField(
        "models.Professions", related_name="profession", null=False
    )
    avg_rating = fields.FloatField(default=0)
    hourly_rate = fields.FloatField(null=False)
    worker_bio = fields.TextField(null=False)
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()

    class PydanticMeta:
        exclude = ["created_at", "modified_at"]


class Professions(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=20, unique=True)
    description = fields.TextField(null=True)
    estimated_time_hours = fields.FloatField(null=True)
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()
    created_by: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="created_by_user", null=False
    )
    modified_by: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="modified_by_user", null=False
    )

    class PydanticMeta:
        exclude = ["id", "created_at", "modified_at", "created_by", "modified_by"]


class Works(models.Model):
    id = fields.IntField(pk=True)
    tags = ArrayField(null=True, element_type="text")
    user_description = fields.TextField(null=True)
    profession: fields.ForeignKeyRelation[Professions] = fields.ForeignKeyField(
        "models.Professions", related_name="work_history", null=False
    )
    scheduled_date = fields.DateField(null=False)
    scheduled_time = fields.TimeField(null=False)
    status = fields.CharField(max_length=20, null=False, default="pending")
    payment_status = fields.CharField(max_length=20, null=False, default="pending")
    estimated_cost = fields.FloatField(null=False)
    final_cost = fields.FloatField(null=True)
    booked_by: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="booked_by", null=False
    )
    assigned_to: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="assigned_to", null=False
    )
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()


class Reviews(models.Model):
    id = fields.IntField(pk=True)
    rating = fields.IntField(null=False)  # 1 to 5
    review = fields.TextField(null=True)
    edited = fields.BooleanField(null=False, default=False)
    work: fields.ForeignKeyRelation[Works] = fields.ForeignKeyField(
        "models.Works", related_name="work", null=False
    )
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="user_id", null=False
    )
    worker: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        "models.Users", related_name="worker_id", null=False
    )
    created_at = fields.DatetimeField()
    modified_at = fields.DatetimeField()

    class PydanticMeta:
        exclude = ["created_at", "modified_at"]

