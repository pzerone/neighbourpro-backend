from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "City" TYPE VARCHAR(50) USING "City"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "Pincode" TYPE INT USING "Pincode"::INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "City" TYPE INT USING "City"::INT;
        ALTER TABLE "users" ALTER COLUMN "Pincode" TYPE VARCHAR(50) USING "Pincode"::VARCHAR(50);"""
