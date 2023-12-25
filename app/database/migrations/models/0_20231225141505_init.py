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
    "is_worker" BOOL NOT NULL  DEFAULT False,
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
    "modified_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "users"."id" IS 'Auto generated';
COMMENT ON COLUMN "users"."username" IS 'Should be a uuid and internal only. not for front end.';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
