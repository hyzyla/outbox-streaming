from pydantic import BaseSettings


class Config(BaseSettings):
    DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/outbox'
    KAFKA_SERVERS = 'localhost:9092'


config = Config()
