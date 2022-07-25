import pytest
import sqlalchemy as sa
import sqlalchemy.orm
import sqlalchemy.exc
from dirty_equals import IsDatetime

from outbox_streaming.kafka.sqlalchemy import SQLAlchemyKafkaOutbox


def test_save_without_connection_or_session(outbox):
    with pytest.raises(ValueError) as e:
        outbox.save(
            topic='test-topic',
            value=b'abcd',
        )


def test_save_when_table_not_exists(outbox, db_connection):
    # table not exists
    with pytest.raises(sa.exc.ProgrammingError):
        outbox.save(
            topic='test-topic',
            value=b'abcd',
            connection=db_connection
        )


def test_save_with_connection_argument(outbox, db_cleanup, db_connection):
    outbox.storage.create_tables()
    outbox.save(
        topic='test-topic',
        value=b'abcd',
        connection=db_connection,
    )
    result = db_connection.execute(sa.select(outbox.storage.model))
    rows = result.all()
    assert len(rows) == 1
    assert dict(rows[0]) == {
        'id': 1,
        'key': None,
        'topic': 'test-topic',
        'value': b'abcd',
        'created_at': IsDatetime(),
    }


def test_save_with_session_argument(outbox, db_cleanup, db_session):
    outbox.storage.create_tables()
    outbox.save(
        topic='test-topic',
        value=b'abcd',
        session=db_session,
    )

    result = db_session.execute(sa.select(outbox.storage.model))
    rows = result.scalars().all()
    row = rows[0]
    print(row)
    assert row.id == 1
    assert row.key is None
    assert row.topic == 'test-topic'
    assert row.value == b'abcd'
    assert row.created_at == IsDatetime()


def test_save_with_scoped_session(config, db_engine, db_cleanup):
    session_factory = sa.orm.sessionmaker(bind=db_engine)
    scoped_session = sa.orm.scoped_session(session_factory)
    try:
        outbox = SQLAlchemyKafkaOutbox(
            engine=db_engine,
            kafka_servers=config['KAFKA_SERVERS'].split(','),
            scoped_session=scoped_session,
        )
        outbox.storage.create_tables()

        outbox.save(
            topic='test-topic',
            value=b'abcd',
        )

        result = scoped_session.execute(sa.select(outbox.storage.model))
        rows = result.scalars().all()
        row = rows[0]
        print(row)
        assert row.id == 1
        assert row.key is None
        assert row.topic == 'test-topic'
        assert row.value == b'abcd'
        assert row.created_at == IsDatetime()

    finally:
        scoped_session.remove()

