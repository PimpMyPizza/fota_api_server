from pydantic import BaseModel


class SchemaGetFirmwareInfoResponse(BaseModel):
    version: str
    number_of_chunks: int

    class Config:
        from_attributes = True

    def __str__(self) -> str:
        return f"{self.version}"


class SchemaGetFirmwareChunkResponse(BaseModel):
    data: str

    class Config:
        from_attributes = True

    def __str__(self) -> str:
        return f"chunk id:{self.int}"
