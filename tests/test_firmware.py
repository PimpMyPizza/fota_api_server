import os
from logging.handlers import RotatingFileHandler
import pytest
from fastapi.testclient import TestClient
from api.main import app
from res.add_firmware_version import add_firmware
from api.core.config import config
import logging

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

client = TestClient(app)
headers = {
    "Authorization": f"Bearer useless_token",
    "accept": "application/json",
}


class TestFirmwareEndpoints:
    firmware_version = "test.1.0.0"
    number_of_chunks = 3

    @pytest.fixture(scope="module", autouse=True)
    def setup_files(self):
        # Create the necessary directories and files before all tests in this module
        firmware_path = f"{config.firmware_base_path}{self.firmware_version}/"
        os.makedirs(firmware_path, exist_ok=True)

        for i in range(self.number_of_chunks):
            # Create the firmware chunk files
            with open(f"{firmware_path}{i+1}.hex", 'w') as file1:
                file1.write(f"Sample firmware data for chunk {i}.")

        # Create the according database firmware info for the firmware
        add_firmware(
            mongo_url="mongodb://localhost:27017",
            db_name=config.database_name,
            firmware_path=firmware_path,
            firmware_version=self.firmware_version,
        )

        yield  # This allows the tests to run

        # Cleanup after all tests in this module
        for i in range(self.number_of_chunks):
            try:
                os.remove(f"{firmware_path}/{i+1}.hex")
            except FileNotFoundError:
                pass
        os.removedirs(firmware_path)

    def test_get_api_version(self):
        response = client.get("/api/api-version")
        assert response.status_code == 200
        res = response.json()
        assert "version" in res

    def test_get_latest_firmware_info(self):
        response = client.get("/api/firmware/info", headers=headers)
        assert response.status_code == 200
        res = response.json()
        assert "version" in res
        assert self.firmware_version == res["version"]
        assert "number_of_chunks" in res

    # def test_get_firmware_chunk(self):
    #     url = f"/api/firmware/chunk?chunk_number=2&version={self.firmware_version}"
    #     response = client.get(url, headers=headers)
    #     assert response.status_code == 200
    #     res = response.json()
    #     assert "data" in res
