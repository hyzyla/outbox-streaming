from time import sleep

from outbox_streaming.kafka.sqlalchemy import SQLAlchemyKafkaOutboxStorage
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/outbox'


engine = create_engine(DATABASE_URL, future=True)
metadata = MetaData(bind=engine)

session = scoped_session(sessionmaker(bind=engine))

storage = SQLAlchemyKafkaOutboxStorage(engine=engine, scoped_session=session)
storage.create_tables()


# create event
storage.save(topic='test-topic', value='1')
storage.save(topic='test-topic', value='2')
session.commit()


for batch in storage.get_messages_batch(size=10):
    print(batch)
    sleep(3)
