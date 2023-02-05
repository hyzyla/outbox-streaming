# outbox-streaming

Reliably send messages to message/task brokers, like Kafka or Celery

**WARNING**:
This project is in early development stage. It's not 
recommended for production use. ⚠️ ☢️ ️🚧

## Roadmap
### Done
* ✅ Kafka + SQLAlchemy
* ✅ Kafka + SQLAlchemy + asyncio
### In progress (lack of tests)
* 🚧 Celery + SQLAlchemy
* 🚧 Celery + SQLAlchemy + asyncio
* 🚧 Custom + SQLAlchemy
* 🚧 Custom + SQLAlchemy + asyncio
* 🚧 RQ + SQLAlchemy
* 🚧 RQ + SQLAlchemy + asyncio
### Planned
* 🔍 Kafka + Django ORM
* 🔍 Celery + Django ORM
* 🔍 RQ + Django ORM
* 🔍 Custom + Django ORM



# Installation
```shell
pip install outbox-streaming
```


# Example FastAPI + Kafka + SQLAlchemy
```python
from fastapi import FastAPI
from outbox_streaming.kafka.sqlalchemy import SQLAlchemyKafkaOutbox
from sqlalchemy import orm

from app import models, db
from app.config import config
from app.schemas import TodoCreate

app = FastAPI()

# create instance of SQLAlchemyKafkaOutbox
outbox = SQLAlchemyKafkaOutbox(
    engine=db.engine,
    kafka_servers=config.KAFKA_SERVERS,
)

# Run separate tread that monitor outbox table and publish messages to Kafka. It's not recommended for production,
# but it's handy for development
outbox.publisher.run_daemon()

Session = orm.sessionmaker(bind=db.engine)

# create outbox tables 
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
        
    # publisher will pick up kafka message from outbox table and will send it kafka topic

    return "OK"

```
