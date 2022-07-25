import pytest
from dotenv import dotenv_values
import os
from typing import Iterator

import pytest
import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm
from sqlalchemy import create_engine

from outbox_streaming.kafka.sqlalchemy import SQLAlchemyKafkaOutbox


@pytest.fixture(scope="session")
def config():
    config = dotenv_values(".env")
    return config


@pytest.fixture()
def db_engine(config):
    engine = create_engine(url=config['DATABASE_URL'], future=True)
    yield engine


@pytest.fixture()
def outbox(config, db_engine) -> SQLAlchemyKafkaOutbox:
    outbox = SQLAlchemyKafkaOutbox(
        engine=db_engine,
        kafka_servers=config['KAFKA_SERVERS'].split(','),
    )
    yield outbox


@pytest.fixture()
def db_cleanup(db_engine) -> None:
    """Automatically cleanup database after every tests"""
    try:
        yield
    finally:
        with db_engine.begin() as connection:
            inspect = sa.inspect(db_engine)
            tables = inspect.get_table_names()
            if tables:
                tables_str = ', '.join(tables)
                connection.execute(sa.text(f"DROP TABLE IF EXISTS {tables_str};"))


@pytest.fixture()
def db_connection(db_engine) -> sa.engine.Connection:
    with db_engine.connect() as connection:
        yield connection


@pytest.fixture()
def db_session(db_engine) -> sa.orm.Session:
    session = sa.orm.sessionmaker(bind=db_engine)
    s: sa.orm.Session = session()
    try:
        yield s
    finally:
        s.close()

