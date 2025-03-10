import logging

from api.models.user import User
from api.core.database import engine


logger = logging.getLogger(__name__)


async def insert_user(data: User) -> User:
    logger.info(f"Insert new user {data.username}")
    user = await engine.save(data)
    return user


async def get_user_by_username(username: str) -> User:
    user = await engine.find_one(User, User.username == username)
    return user


async def get_user_by_email(email: str) -> User:
    user = await engine.find_one(User, User.email == email)
    return user


async def get_user_by_user_id(user_id: str) -> User:
    user = await engine.find_one(User, User.id == user_id)
    return user
