import sqlalchemy as sa
from fastapi import FastAPI
from outbox_streaming.main import SQLAlchemyKafkaOutbox
from sqlalchemy import orm

from app import models, db
from app.config import config
from app.schemas import TodoCreate

app = FastAPI()
outbox = SQLAlchemyKafkaOutbox(
    metadata=db.Base.metadata,
    engine=db.engine,
    kafka_servers=config.KAFKA_SERVERS,
)

Session = orm.sessionmaker(bind=db.engine)

# create all tables for test environment
db.Base.metadata.create_all(bind=db.engine)


@app.post('/todos')
def create_todo(create: TodoCreate) -> None:

    with db.engine.begin() as connection:

        # create new object
        result = connection.execute(
            sa.insert(models.Todo.__table__)
            .values(text=create.text)
            .returning(models.Todo.__table__)
        )
        row = result.fetchone()

        # create kafka event in outbox table
        outbox.save(
            connection=connection,
            topic='todo_created',
            value=dict(row),
        )
