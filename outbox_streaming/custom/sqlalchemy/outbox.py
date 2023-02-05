import sqlalchemy as sa
import sqlalchemy.orm

from ...common.types import JsonDumpFunction
from ..publisher import OutboxCustomPublisher
from .storage import SQLAlchemyCustomOutboxStorage


class SQLAlchemyCustomOutbox:

    storage_class = SQLAlchemyCustomOutboxStorage
    publisher_class = OutboxCustomPublisher

    def __init__(
        self,
        engine: sa.engine.Engine,
        json_dump: JsonDumpFunction | None = None,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(
            engine=engine, json_dump=json_dump, scoped_session=scoped_session
        )
        self.publisher = self.publisher_class(storage=self.storage)
        self.save = self.storage.save
