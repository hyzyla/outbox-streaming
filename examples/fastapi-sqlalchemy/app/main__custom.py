from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

import sqlalchemy as sa
from fastapi import FastAPI
from outbox_streaming.main import SQLAlchemyKafkaOutboxStorage, SQLAlchemyKafkaOutbox
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from app import models, db
from app.config import config
from app.schemas import TodoCreate

app = FastAPI()

connection_var = ContextVar('connection_var')


class OutboxStorage(SQLAlchemyKafkaOutboxStorage):

    def get_connection(
        self,
        session: Optional[Session] = None,
        connection: Optional[Connection] = None,
    ) -> Connection:
        """ Trying to get connection from context var """
        return connection_var.get()


class Outbox(SQLAlchemyKafkaOutbox):
    storage_class = OutboxStorage


outbox = Outbox(
    metadata=db.Base.metadata,
    engine=db.engine,
    kafka_servers=config.KAFKA_CONFIG
)


# create all tables for test environment
db.Base.metadata.create_all(bind=db.engine)


@contextmanager
def start_transaction():
    with db.engine.begin() as connection:
        token = connection_var.set(connection)
        try:
            yield connection
        finally:
            connection_var.reset(token)


def insert_todo(text: str):

    connection = connection_var.get()

    # create new object
    result = connection.execute(
        sa.insert(models.Todo.__table__)
        .values(text=text)
        .returning(models.Todo.__table__)
    )
    row = result.fetchone()
    return row


@app.post('/todos')
def create_todo(create: TodoCreate) -> None:

    with start_transaction():

        row = insert_todo(text=create.text)

        outbox.save(topic='todo_created', value=dict(row))
