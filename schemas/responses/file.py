from pydantic import BaseModel, ConfigDict


class FileResponse(BaseModel):
    status: str
    file_id: int
    filename: str
    saved_as: str
    size: int
    download_url: str

    model_config = ConfigDict(from_attributes=True)
