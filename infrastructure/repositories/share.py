from sqlalchemy.ext.asyncio import AsyncSession
from domain.share.entities import Share

class ShareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, file_id):
        pass

    @staticmethod
    def __convert_to_entity(share) -> Share:
        return Share(
            id=file.id,
            hash_name=file.hash_name,
            original_filename=file.original_filename,
            type=file.type,
            owner=file.owner,
            path=file.path,
            size=file.size,
            created_at=file.created_at,
        )