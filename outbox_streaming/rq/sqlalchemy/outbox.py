from typing import Optional

import sqlalchemy as sa
import sqlalchemy.orm

from .storage import SQLAlchemyRQOutboxStorage
from ..publisher import OutboxRQPublisher


class SQLAlchemyRQOutbox:

    storage_class = SQLAlchemyRQOutboxStorage
    publisher_class = OutboxRQPublisher

    def __init__(
        self,
        engine: sa.engine.Engine,
        scoped_session: Optional[sa.orm.scoped_session] = None,
    ) -> None:
        self.storage = self.storage_class(engine=engine, scoped_session=scoped_session)
        self.publisher = self.publisher_class(
            storage=self.storage,
        )
        self.save = self.storage.save
