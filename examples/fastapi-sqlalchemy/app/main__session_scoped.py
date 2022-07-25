from fastapi import FastAPI
from outbox_streaming.main import SQLAlchemyKafkaOutbox
from sqlalchemy import orm

from app import models, db
from app.config import config
from app.schemas import TodoCreate

app = FastAPI()

Session = orm.sessionmaker(bind=db.engine)
ScopedSession = orm.scoped_session(Session)

outbox = SQLAlchemyKafkaOutbox(
    metadata=db.Base.metadata,
    engine=db.engine,
    scoped_session=ScopedSession,  # scoped session passed to init method
    kafka_servers=config.KAFKA_SERVERS,
)
# create all tables for test environment
db.Base.metadata.create_all(bind=db.engine)


@app.post('/todos')
def create_todo(create: TodoCreate) -> None:

    # create new object
    todo = models.Todo(text=create.text)
    ScopedSession.add(todo)

    # create kafka event in outbox table. Please note that we are not passing any
    # session into method call, scoped_session is passed to init method of outbox
    # instance
    outbox.save(
        topic='todo_created',
        value=todo.to_dict(),
    )

    # commit changes in database
    ScopedSession.commit()
    ScopedSession.remove()
