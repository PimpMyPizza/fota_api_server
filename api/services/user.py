from api.crud import user as col_user
from fastapi import HTTPException
import logging


logger = logging.getLogger(__name__)


async def get_user_full_name(username: str) -> str:
    user = await col_user.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    prefix = f"{user.title} " if user.title and user.title != "" else ""
    first_letter_of_fn = f"{user.first_name[0].capitalize()}. " if user.first_name and user.first_name != "" else ""
    return f"{prefix}{first_letter_of_fn}{user.last_name}"
