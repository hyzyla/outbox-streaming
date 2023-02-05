import sqlalchemy as sa
import sqlalchemy.orm

from ..publisher import OutboxRQPublisher
from .storage import SQLAlchemyRQOutboxStorage


class SQLAlchemyRQOutbox:

    storage_class = SQLAlchemyRQOutboxStorage
    publisher_class = OutboxRQPublisher

    def __init__(
        self,
        engine: sa.engine.Engine,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.storage = self.storage_class(engine=engine, scoped_session=scoped_session)
        self.publisher = self.publisher_class(
            storage=self.storage,
        )
        self.save = self.storage.save
