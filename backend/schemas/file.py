from pydantic import BaseModel


class FileId(BaseModel):
    id: int

class FileResponseSchema(BaseModel):
    status: str
    file_id: int
    filename: str
    saved_as: str
    size: int
    download_url: str

    class Config:
        from_attributes = True