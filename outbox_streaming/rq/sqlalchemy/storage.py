from typing import Any, Iterator

import sqlalchemy as sa
import sqlalchemy.orm

from ...common.sqlachemy.storage import SQLAlchemyStorageMixin
from ..types import RQMessage, RQOutboxStorageABC
from .models import OutboxRQModel


class SQLAlchemyRQOutboxStorage(RQOutboxStorageABC, SQLAlchemyStorageMixin):

    model = OutboxRQModel

    def __init__(
        self,
        engine: sa.engine.Engine,
        scoped_session: sa.orm.scoped_session | None = None,
    ) -> None:
        self.engine: sa.engine.Engine = engine
        self.scoped_session: sa.orm.scoped_session | None = scoped_session

    def save(
        self,
        func: str,
        args: list[Any],
        kwargs: dict[str, str],
        session: sa.orm.Session | None = None,
        connection: sa.engine.Connection | None = None,
    ) -> None:
        """Serialize and save to database RQ message"""

        connection = self.get_connection(
            session=session,
            connection=connection,
        )

        # TODO: add args and kwargs serialization
        connection.execute(
            sa.insert(self.model).values(
                func=func,
                args=args,
                kwargs=kwargs,
            )
        )

    def get_messages_batch(self, size: int) -> Iterator[list[RQMessage]]:

        query = self.model.consume_query(size=size)

        # Create connection to database
        with self.engine.connect() as connection:

            # get new messages from table forever
            while True:

                # for every batch create new transaction
                with connection.begin():
                    result = connection.execute(query)
                    rows = result.fetchall()
                    yield [
                        RQMessage(
                            id=row["id"],
                            func=row["func"],
                            args=row["args"],
                            kwargs=row["kwargs"],
                        )
                        for row in rows
                    ]
