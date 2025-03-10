from api.models.user import AuthUser, Role
from fastapi import HTTPException
from api.core.config import config
from api.crud import firmware as col_firmware
import logging

from api.schemas.firmware import SchemaGetFirmwareInfoResponse, SchemaGetFirmwareChunkResponse

logger = logging.getLogger(__name__)


async def get_firmware_info(user: AuthUser) -> SchemaGetFirmwareInfoResponse:
    if Role.default not in user.roles:
        er_msg = f"User {user.username} has no right to access firmwares"
        logger.error(er_msg)
        raise HTTPException(status_code=403, detail=er_msg)
    f = await col_firmware.get_latest_firmware()
    if not f:
        er_msg = f"User {user.username} has no right to access firmwares"
        logger.error(er_msg)
        raise HTTPException(status_code=403, detail=er_msg)
    return SchemaGetFirmwareInfoResponse(
        version=f.version,
        number_of_chunks=f.number_of_chunks,
    )


async def get_firmware_chunk(user: AuthUser, version: str, chunk_number: int) -> SchemaGetFirmwareChunkResponse:
    if Role.default not in user.roles:
        er_msg = f"User {user.username} has no right to access firmware {version}"
        logger.error(er_msg)
        raise HTTPException(status_code=403, detail=er_msg)
    f = await col_firmware.get_firmware_by_version(version=version)
    if not f:
        er_msg = f"User {user.username} has no right to access firmware {version}"
        logger.error(er_msg)
        raise HTTPException(status_code=403, detail=er_msg)
    if chunk_number > f.number_of_chunks:
        raise HTTPException(status_code=404, detail=f"Firmware {f.version} has only {f.number_of_chunks} chunks")
    with open(f"{config.firmware_base_path}{f.version}/{chunk_number}.hex", "r") as file:
        data = file.read()
    return SchemaGetFirmwareChunkResponse(data=data)
