from typing import Optional

from sqlalchemy.ext.asyncio import AsyncEngine, async_scoped_session

from .storage import AsyncSQLAlchemyRQOutboxStorage
from ..publisher import AsyncOutboxRQPublisher


class AsyncSQLAlchemyRQOutbox:

    storage_class = AsyncSQLAlchemyRQOutboxStorage
    publisher_class = AsyncOutboxRQPublisher

    def __init__(
        self,
        engine: AsyncEngine,
        scoped_session: Optional[async_scoped_session] = None,
    ) -> None:
        self.storage = self.storage_class(engine=engine, scoped_session=scoped_session)
        self.publisher = self.publisher_class(
            storage=self.storage,
        )
        self.save = self.storage.save
