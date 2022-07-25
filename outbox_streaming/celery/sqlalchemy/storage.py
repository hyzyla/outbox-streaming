from typing import Any, Iterable, Iterator, List, Mapping, Optional

import sqlalchemy as sa
import sqlalchemy.orm
from celery import Task

from ...common.sqlachemy.storage import SQLAlchemyStorageMixin
from ..types import CeleryOutboxStorageABC, CeleryTask
from .models import OutboxCeleryModel


class SQLAlchemyCeleryOutboxStorage(CeleryOutboxStorageABC, SQLAlchemyStorageMixin):

    model = OutboxCeleryModel

    def __init__(
        self,
        engine: sa.engine.Engine,
        scoped_session: Optional[sa.orm.scoped_session] = None,
    ) -> None:
        self.engine: sa.engine.Engine = engine
        self.scoped_session: Optional[sa.orm.scoped_session] = scoped_session

    def save(
        self,
        task: Task,
        args: Optional[Iterable[Any]] = None,
        kwargs: Optional[Mapping[str, Any]] = None,
        options: Optional[Mapping[str, Any]] = None,
        session: Optional[sa.orm.Session] = None,
        connection: Optional[sa.engine.Connection] = None,
    ) -> None:
        """Serialize and save to database Celery task"""

        connection = self.get_connection(
            session=session,
            connection=connection,
        )

        connection.execute(
            sa.insert(self.model).values(
                name=task.name,
                args=args,
                kwargs=kwargs,
                options=options,
            )
        )

    def get_tasks_batch(self, size: int) -> Iterator[List[CeleryTask]]:

        query = self.model.consume_query(size=size)

        # Create connection to database
        with self.engine.connect() as connection:

            # get new tasks from table forever
            while True:

                # for every batch create new transaction
                with connection.begin():
                    result = connection.execute(query)
                    rows = result.fetchall()
                    yield [
                        CeleryTask(
                            id=row["id"],
                            name=row["name"],
                            args=row["args"],
                            kwargs=row["kwargs"],
                            options=row["options"],
                        )
                        for row in rows
                    ]
