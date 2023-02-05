import celery
import pytest
import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm
from dirty_equals import IsDatetime

from outbox_streaming.celery.sqlalchemy import SQLAlchemyCeleryOutbox


@pytest.fixture()
def outbox(config, db_engine, celery_app) -> SQLAlchemyCeleryOutbox:
    outbox = SQLAlchemyCeleryOutbox(
        engine=db_engine,
        app=celery_app,
    )
    yield outbox


@pytest.fixture()
def celery_task(celery_app):
    @celery_app.task
    def task_for_test(x, y):
        return x * y

    return task_for_test


def test_save_without_connection_or_session(
    outbox: SQLAlchemyCeleryOutbox, celery_task: celery.Task
):

    with pytest.raises(ValueError) as e:
        outbox.save(
            task=celery_task,
            args=(2, 3),
        )


def test_save_when_table_not_exists(outbox, db_connection, celery_task: celery.Task):

    # table not exists
    with pytest.raises(sa.exc.ProgrammingError):
        outbox.save(
            task=celery_task,
            args=(2, 3),
            connection=db_connection,
        )


def test_save_with_connection_argument(
    outbox, db_cleanup, db_connection, celery_task: celery.Task
):
    outbox.storage.create_tables()
    outbox.save(
        task=celery_task,
        args=(2, 3),
        connection=db_connection,
    )
    result = db_connection.execute(sa.select(outbox.storage.model))
    rows = result.all()
    assert len(rows) == 1
    assert dict(rows[0]) == {
        "id": 1,
        "created_at": IsDatetime(),
        "name": "test_celery_sqlachemy.task_for_test",
        "args": [2, 3],
        "kwargs": None,
        "options": None,
    }


def test_save_with_session_argument(
    outbox, db_cleanup, db_session, celery_task: celery.Task
):
    outbox.storage.create_tables()
    outbox.save(
        task=celery_task,
        args=(2, 3),
        session=db_session,
    )

    result = db_session.execute(sa.select(outbox.storage.model))
    rows = result.scalars().all()
    assert len(rows) == 1
    assert rows[0].to_dict() == {
        "id": 1,
        "created_at": IsDatetime(),
        "name": "test_celery_sqlachemy.task_for_test",
        "args": [2, 3],
        "kwargs": None,
        "options": None,
    }


def test_save_with_scoped_session(
    config, db_engine, db_cleanup, celery_app, celery_task
):
    session_factory = sa.orm.sessionmaker(bind=db_engine)
    scoped_session = sa.orm.scoped_session(session_factory)
    try:
        outbox = SQLAlchemyCeleryOutbox(
            engine=db_engine,
            app=celery_app,
            scoped_session=scoped_session,
        )
        outbox.storage.create_tables()

        outbox.save(
            task=celery_task,
            args=(2, 3),
        )

        result = scoped_session.execute(sa.select(outbox.storage.model))
        rows = result.scalars().all()
        print(rows)
        assert len(rows) == 1
        assert rows[0].to_dict() == {
            "id": 1,
            "created_at": IsDatetime(),
            "name": "test_celery_sqlachemy.task_for_test",
            "args": [2, 3],
            "kwargs": None,
            "options": None,
        }

    finally:
        scoped_session.remove()
