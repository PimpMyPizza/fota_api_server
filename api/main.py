import logging
from logging.handlers import RotatingFileHandler
from api.core.config import config
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from api.routes import firmware


logging.basicConfig(
    level=config.log_level,
    format=config.log_format,
    handlers=[
        logging.StreamHandler(),  # Log to console
        RotatingFileHandler(  # Log to file also
            config.log_output_file,
            maxBytes=5*1024*1024,
            backupCount=4
        ),
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"API",
    version=config.api_version,
)
app.include_router(firmware.router, prefix=f"{config.api_prefix}/firmware", tags=["Firmware"])


# Serve profile pictures from the "profile_pictures" directory
app.mount(
    path=f"{config.api_prefix}/firmware",
    app=StaticFiles(directory=config.firmware_base_path),
    name="firmware",
)

origins = [
    "*",  # TODO: adapt later in production mode
]

app.add_middleware(
    # noqa
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{config.api_prefix}/api-version", tags=["API"])
async def api_version():
    return {"version": config.api_version}


if __name__ == "__main__":
    import uvicorn

    docs_url = f"http{'s' if config.ssl_key_file != '' else ''}://{config.api_host}:{config.api_port}/docs"
    logger.info(f"Go to {docs_url} for a description of the endpoints.")

    uvicorn.run(
        app="main:app",
        host=config.api_host,
        port=config.api_port,
        ssl_keyfile=None if config.ssl_key_file == "" else config.ssl_key_file,
        ssl_certfile=None if config.ssl_cert_file == "" else config.ssl_cert_file,
    )
