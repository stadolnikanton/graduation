from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.share.entities import ShareLink
from infrastructure.database.share import ShareLinkDB


class ShareRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, share_link: ShareLink) -> ShareLink:
        new_share_link = ShareLinkDB(
            token=share_link.token,
            file_id=share_link.file_id,
            expires_at=share_link.expires_at,
            max_downloads=share_link.max_downloads,
            download_count=share_link.download_count,
        )
        self.session.add(new_share_link)

        await self.session.commit()
        await self.session.refresh(new_share_link)

        return ShareRepository.__convert_to_entity(new_share_link)
    
    async def get_file_by_token(self, token) -> ShareLink | None: 
        stmt = select(ShareLinkDB).where(ShareLinkDB.token == token)
        result = await self.session.execute(stmt)
        
        share = result.scalar_one_or_none()
        
        if share:
            return ShareRepository.__convert_to_entity(share)
        return None

    async def delete_file_by_token(self, token):
        stmt = select(ShareLinkDB).where(ShareLinkDB.token == token)
        result = await self.session.execute(stmt)
        
        share = result.scalar_one_or_none()

        if share:
            await self.session.delete(share)
            await self.session.commit()

            return ShareRepository.__convert_to_entity(share)

        return False

    @staticmethod
    def __convert_to_entity(share) -> ShareLink:
        return ShareLink(
            id=share.id,
            token=share.token,
            file_id=share.file_id,
            expires_at=share.expires_at,
            max_downloads=share.max_downloads,
            download_count=share.download_count,
            created_at=share.created_at,
        )
