from odmantic import Model


class Firmware(Model):
    version: str
    path: str
    number_of_chunks: int
    number: int
    model_config = {
        "collection": "firmwares"
    }

    def __str__(self) -> str:
        return f"{self.version} ({self.path})"
