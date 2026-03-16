from pydantic import BaseModel


class ShareRequest(BaseModel):
    user_id: int
