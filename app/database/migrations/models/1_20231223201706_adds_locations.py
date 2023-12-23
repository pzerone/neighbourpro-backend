from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "State" VARCHAR(50);
        ALTER TABLE "users" ADD "City" INT;
        ALTER TABLE "users" ADD "Longitude" DECIMAL(9,6);
        ALTER TABLE "users" ADD "Latitude" DECIMAL(9,6);
        ALTER TABLE "users" ADD "Pincode" VARCHAR(50);
        ALTER TABLE "users" ADD "House_name" VARCHAR(50);
        ALTER TABLE "users" ADD "Street" VARCHAR(50);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP COLUMN "State";
        ALTER TABLE "users" DROP COLUMN "City";
        ALTER TABLE "users" DROP COLUMN "Longitude";
        ALTER TABLE "users" DROP COLUMN "Latitude";
        ALTER TABLE "users" DROP COLUMN "Pincode";
        ALTER TABLE "users" DROP COLUMN "House_name";
        ALTER TABLE "users" DROP COLUMN "Street";"""
