from fastapi import FastAPI
from outbox_streaming.kafka.sqlalchemy import SQLAlchemyKafkaOutbox
from sqlalchemy import orm

from app import models, db
from app.config import config
from app.schemas import TodoCreate

app = FastAPI()

outbox = SQLAlchemyKafkaOutbox(
    engine=db.engine,
    kafka_servers=config.KAFKA_SERVERS,
)
outbox.publisher.run_daemon()

Session = orm.sessionmaker(bind=db.engine)

# create all tables for test environment
db.Base.metadata.create_all(bind=db.engine)
outbox.storage.create_tables(engine=db.engine)


@app.post('/todos')
def create_todo(create: TodoCreate) -> str:

    with Session() as session:

        # create new object
        todo = models.Todo(text=create.text)
        session.add(todo)

        # create kafka event in outbox table
        outbox.save(
            session=session,
            topic='todo_created',
            value=todo.to_dict(),
        )

        # commit changes in database
        session.commit()


    return "OK"
