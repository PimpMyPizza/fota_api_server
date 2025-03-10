import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import logging


logger = logging.getLogger(__name__)


class Config(BaseSettings):
    is_production: bool
    is_test: bool

    # API settings
    api_version: str
    api_host: str
    api_port: int
    api_prefix: str = "/api"

    # SSL stuff
    ssl_key_file: str = None
    ssl_cert_file: str = None

    # Keycloak Settings
    keycloak_server_url: str
    keycloak_client_id: str
    keycloak_client_secret: str
    keycloak_public_key_url: str

    database_url: str
    database_name: str

    # Token Settings
    secret_key: str
    jwt_token_algorithm: str

    # Logging
    log_level: str
    log_format: str
    log_output_file: str

    # Date and Time
    datetime_format: str = "%Y-%m-%dT%H:%M:%S.%f%z"

    # storage
    firmware_base_path: str


# Load the base .env file first
load_dotenv(".env")

# Get the value of APP_ENV (default to 'prod' if not set)
API_ENV = os.getenv('API_ENV', '.env')

logger.info(f"Load environment variables from {API_ENV}")

load_dotenv(API_ENV, override=True)

# Instantiate settings object
config = Config()
