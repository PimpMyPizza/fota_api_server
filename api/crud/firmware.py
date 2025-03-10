import logging

from odmantic.query import desc

from api.models.firmware import Firmware
from api.core.database import engine


logger = logging.getLogger(__name__)


async def insert_firmware(data: Firmware) -> Firmware:
    logger.info(f"Insert firmware version {data.version}")
    user = await engine.save(data)
    return user


async def get_firmware_by_version(version: str) -> Firmware:
    firmware = await engine.find_one(Firmware, Firmware.version == version)
    return firmware


async def get_latest_firmware() -> Firmware:
    firmware = await engine.find_one(Firmware, sort=desc(Firmware.number))
    return firmware
