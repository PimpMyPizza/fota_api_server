from fastapi import Depends, status, APIRouter, HTTPException
from api.models.user import AuthUser
from api.services.auth import verify_token_with_keycloak
from api.services.firmware import get_firmware_info, get_firmware_chunk
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/info")
async def get_firmware_info_endpoint(current_user: AuthUser = Depends(verify_token_with_keycloak)):
    try:
        return await get_firmware_info(user=current_user)
    except Exception as e:
        logger.error(e)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/chunk")
async def get_firmware_chunk_endpoint(chunk_number: int, version: str, current_user: AuthUser = Depends(verify_token_with_keycloak)):
    try:
        return await get_firmware_chunk(user=current_user, chunk_number=chunk_number, version=version)
    except Exception as e:
        logger.error(e)
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
