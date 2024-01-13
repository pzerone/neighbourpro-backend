from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "professions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL UNIQUE,
    "description" TEXT,
    "estimated_time_hours" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50),
    "role" VARCHAR(10) NOT NULL  DEFAULT 'user',
    "hourly_rate" DOUBLE PRECISION,
    "worker_bio" TEXT,
    "email" VARCHAR(100) NOT NULL,
    "phone_number" VARCHAR(20) NOT NULL,
    "password_hash" VARCHAR(128) NOT NULL,
    "House_name" VARCHAR(50),
    "Street" VARCHAR(50),
    "City" VARCHAR(50),
    "State" VARCHAR(50),
    "Pincode" INT,
    "Latitude" DECIMAL(9,6),
    "Longitude" DECIMAL(9,6),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "profession_id" INT REFERENCES "professions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "reviews" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "rating" INT NOT NULL,
    "review" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "user_id_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "worker_id_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "works" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tags" text[],
    "user_description" TEXT,
    "scheduled_date" DATE,
    "scheduled_time" TIMETZ,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "payment_status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "estimated_cost" DOUBLE PRECISION,
    "final_cost" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "assigned_to_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "booked_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "profession_id" INT NOT NULL REFERENCES "professions" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
