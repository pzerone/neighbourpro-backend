from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "workerdetails" ADD "profession_id" INT NOT NULL;
        ALTER TABLE "workerdetails" DROP COLUMN "profession";
        ALTER TABLE "workerdetails" ADD CONSTRAINT "fk_workerde_professi_e3771b38" FOREIGN KEY ("profession_id") REFERENCES "professions" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "workerdetails" DROP CONSTRAINT "fk_workerde_professi_e3771b38";
        ALTER TABLE "workerdetails" ADD "profession" VARCHAR(20) NOT NULL;
        ALTER TABLE "workerdetails" DROP COLUMN "profession_id";"""
