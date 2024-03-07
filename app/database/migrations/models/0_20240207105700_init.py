from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(20) NOT NULL UNIQUE,
    "first_name" VARCHAR(50) NOT NULL,
    "last_name" VARCHAR(50),
    "email" VARCHAR(100) NOT NULL,
    "password" VARCHAR(128) NOT NULL,
    "role" VARCHAR(10) NOT NULL  DEFAULT 'user',
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL
);
CREATE TABLE IF NOT EXISTS "professions" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(20) NOT NULL UNIQUE,
    "description" TEXT,
    "estimated_time_hours" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "created_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "modified_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "userdetails" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "phone_number" VARCHAR(20) NOT NULL,
    "house_name" VARCHAR(50) NOT NULL,
    "street" VARCHAR(50) NOT NULL,
    "city" VARCHAR(50) NOT NULL,
    "state" VARCHAR(50) NOT NULL,
    "pincode" INT NOT NULL,
    "latitude" DECIMAL(9,6) NOT NULL,
    "longitude" DECIMAL(9,6) NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "workerdetails" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "profession" VARCHAR(20) NOT NULL,
    "avg_rating" DOUBLE PRECISION NOT NULL  DEFAULT 0,
    "hourly_rate" DOUBLE PRECISION NOT NULL,
    "worker_bio" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "works" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tags" text[],
    "user_description" TEXT,
    "scheduled_date" DATE NOT NULL,
    "scheduled_time" TIMETZ NOT NULL,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "payment_status" VARCHAR(20) NOT NULL  DEFAULT 'pending',
    "estimated_cost" DOUBLE PRECISION NOT NULL,
    "final_cost" DOUBLE PRECISION,
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "assigned_to_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "booked_by_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "profession_id" INT NOT NULL REFERENCES "professions" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "reviews" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "rating" INT NOT NULL,
    "review" TEXT,
    "edited" BOOL NOT NULL  DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL,
    "modified_at" TIMESTAMPTZ NOT NULL,
    "user_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "work_id" INT NOT NULL REFERENCES "works" ("id") ON DELETE CASCADE,
    "worker_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
