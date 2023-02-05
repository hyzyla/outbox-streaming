import sqlalchemy as sa
import sqlalchemy.orm
from sqlalchemy.ext.asyncio import AsyncEngine

from ....common.types import JsonDumpFunction
from ..publisher import AsyncOutboxCustomPublisher
from .storage import AsyncSQLAlchemyCustomOutboxStorage


class AsyncSQLAlchemyCustomOutbox:

    storage_class = AsyncSQLAlchemyCustomOutboxStorage
    publisher_class = AsyncOutboxCustomPublisher

    def __init__(
        self,
        engine: AsyncEngine,
        json_dump: JsonDumpFunction | None = None,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(
            engine=engine,
            json_dump=json_dump,
            scoped_session=scoped_session,
        )
        self.publisher = self.publisher_class(storage=self.storage)
        self.save = self.storage.save
