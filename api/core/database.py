from motor.motor_asyncio import AsyncIOMotorClient
from api.core.config import config
from odmantic import AIOEngine

client = AsyncIOMotorClient(config.database_url)
engine = AIOEngine(client=client, database=config.database_name)


def init_db():
    # TODO: Add startup checks here
    pass
