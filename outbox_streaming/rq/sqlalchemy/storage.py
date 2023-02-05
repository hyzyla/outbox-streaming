from typing import Any, Iterator, List, Optional

import sqlalchemy as sa
import sqlalchemy.orm

from .models import OutboxRQModel
from ..types import RQMessage, RQOutboxStorageABC
from ...common.sqlachemy.storage import SQLAlchemyStorageMixin


class SQLAlchemyRQOutboxStorage(RQOutboxStorageABC, SQLAlchemyStorageMixin):

    model = OutboxRQModel

    def __init__(
        self,
        engine: sa.engine.Engine,
        scoped_session: Optional[sa.orm.scoped_session] = None,
    ) -> None:
        self.engine: sa.engine.Engine = engine
        self.scoped_session: Optional[sa.orm.scoped_session] = scoped_session

    def save(
        self,
        func: str,
        args: list[Any],
        kwargs: dict[str, str],
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
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

    def get_messages_batch(self, size: int) -> Iterator[List[RQMessage]]:

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
                            args=row["args"],
                            kwargs=row["kwargs"],
                        )
                        for row in rows
                    ]
