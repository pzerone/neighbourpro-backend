from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ADD "profession_id" INT;
        ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(20) USING "username"::VARCHAR(20);
        ALTER TABLE "users" ADD CONSTRAINT "fk_users_professi_9e286866" FOREIGN KEY ("profession_id") REFERENCES "professions" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" DROP CONSTRAINT "fk_users_professi_9e286866";
        ALTER TABLE "users" DROP COLUMN "profession_id";
        ALTER TABLE "users" ALTER COLUMN "username" TYPE VARCHAR(20) USING "username"::VARCHAR(20);"""
