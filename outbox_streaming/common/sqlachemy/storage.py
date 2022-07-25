from typing import Optional, Type

from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, scoped_session

from ...common.sqlachemy.base import OutboxMixin


class SQLAlchemyStorageMixin:

    scoped_session: Optional[scoped_session]
    model: Type[OutboxMixin]
    engine: Engine

    def get_connection(
        self,
        session: Optional[Session] = None,
        connection: Optional[Connection] = None,
    ) -> Connection:
        if connection is not None:
            return connection
        if session is not None:
            return session.connection()
        if self.scoped_session is not None:
            return self.scoped_session.connection()
        raise ValueError(
            "Can not get connection to database. "
            "Provide SQLAlchemy connection or session to .save method "
            "or pass scoped_session to initializer of Outbox class"
        )

    def create_tables(self) -> None:
        self.model.metadata.create_all(bind=self.engine)
